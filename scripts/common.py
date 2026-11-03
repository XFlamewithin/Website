"""Shared helpers for building the site and checking resource links."""

import difflib
import hashlib
import html
import json
import re
import ssl
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOURCES_FILE = ROOT / "resources.toml"
SITE_FILE = ROOT / "site.toml"
STATUS_FILE = ROOT / "data" / "link-status.json"
SNAPSHOT_DIR = ROOT / "data" / "snapshots"
FILES_DIR = ROOT / "files"

# Some sites forget to send part of their security certificate chain (browsers
# quietly work around this). Missing pieces are stored here so checks still work.
EXTRA_CERTS = ROOT / "data" / "extra-intermediate-certs.pem"
SSL_CONTEXT = ssl.create_default_context()
if EXTRA_CERTS.exists():
    SSL_CONTEXT.load_verify_locations(EXTRA_CERTS)

USER_AGENT = "Mozilla/5.0 (compatible; PatientResourceLinkChecker/1.0)"
SECTIONS = {"patients": "For patients", "clinicians": "For clinicians"}

# A resource is hidden from the site (or served only from its saved copy)
# while it has one of these statuses, until it is approved again.
PAUSED = {"changed", "broken"}


def slugify(text):
    text = re.sub(r"['’]", "", text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def load_site():
    return tomllib.loads(SITE_FILE.read_text(encoding="utf-8"))


def load_resources():
    data = tomllib.loads(RESOURCES_FILE.read_text(encoding="utf-8"))
    resources = data.get("resource", [])
    seen = set()
    for i, r in enumerate(resources, 1):
        for field in ("section", "topic", "title", "url"):
            if not r.get(field):
                raise SystemExit(f"resources.toml: resource #{i} is missing '{field}'")
        if r["section"] not in SECTIONS:
            raise SystemExit(f"resources.toml: '{r['title']}' has section '{r['section']}' "
                             f"(must be one of: {', '.join(SECTIONS)})")
        r["id"] = r.get("id") or slugify(r["title"])
        if r["id"] in seen:
            raise SystemExit(f"resources.toml: two resources share the id '{r['id']}' — "
                             "give one of them a different title or an explicit id")
        seen.add(r["id"])
        r.setdefault("check", "auto")
    return resources


def load_status():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    return {}


def save_status(status):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- fetching

class FetchError(Exception):
    def __init__(self, message, permanent):
        super().__init__(message)
        self.permanent = permanent  # True for 404/410/unknown host: the link is gone


def fetch(url):
    """Return (final_url, content_type, body bytes)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=45, context=SSL_CONTEXT) as resp:
            return resp.geturl(), resp.headers.get("Content-Type", ""), resp.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} {e.reason}", permanent=e.code in (404, 410)) from None
    except urllib.error.URLError as e:
        unknown_host = "Name or service not known" in str(e.reason) or "nodename nor servname" in str(e.reason)
        raise FetchError(f"Could not connect: {e.reason}", permanent=unknown_host) from None
    except Exception as e:  # timeouts, connection resets, etc.
        raise FetchError(f"Could not connect: {e}", permanent=False) from None


def is_pdf(content_type, body):
    return "pdf" in content_type.lower() or body[:5] == b"%PDF-"


def page_text(body):
    """Visible text of an HTML page, used to detect meaningful changes."""
    t = body.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|noscript|svg|head|template)\b.*?</\1>", " ", t)
    t = re.sub(r"(?s)<!--.*?-->", " ", t)
    t = re.sub(r"(?i)<(br|p|div|li|h[1-6]|tr|section|article)\b[^>]*>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    lines = (re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in t.split("\n"))
    return "\n".join(line for line in lines if line)


def fingerprint(content_type, body):
    """Return (kind, hash, text snapshot or None)."""
    if is_pdf(content_type, body):
        return "pdf", hashlib.sha256(body).hexdigest(), None
    text = page_text(body)
    if len(text) < 200:
        # App-style page with almost no text (built by JavaScript): compare raw HTML.
        return "page", hashlib.sha256(body).hexdigest(), text
    return "page", hashlib.sha256(text.encode()).hexdigest(), text


def text_diff(old, new, limit=60):
    lines = list(difflib.unified_diff(old.splitlines(), new.splitlines(),
                                      "approved version", "current version", lineterm="", n=1))
    if len(lines) > limit:
        lines = lines[:limit] + [f"... ({len(lines) - limit} more lines of differences)"]
    return "\n".join(lines)


def effective_status(entry):
    """Combine the file's own status with the status of the page it is posted on.

    "withdrawn" means the source page no longer links to the file, so it may
    be outdated: it is hidden from the site entirely, saved copy included.
    """
    page = entry.get("page_status", "ok")
    if page == "unlisted":
        return "withdrawn"
    if entry.get("status") in PAUSED:
        return entry["status"]
    if page in ("changed", "broken"):
        return "changed"
    return entry.get("status", "unchecked")


def _norm(url):
    u = urllib.parse.urlsplit(url)
    host = u.netloc.lower().removeprefix("www.")
    return host, urllib.parse.unquote(u.path).rstrip("/")


def links_to(page_body, page_url, target):
    """True if the page contains a link to the target file."""
    host, path = _norm(target)
    filename = path.rsplit("/", 1)[-1].lower()
    for href in re.findall(r"""href\s*=\s*["']([^"'#]+)""", page_body.decode("utf-8", "replace"), re.I):
        h, p = _norm(urllib.parse.urljoin(page_url, html.unescape(href.strip())))
        if (h, p) == (host, path) or (filename.endswith(".pdf") and p.lower().endswith("/" + filename)):
            return True
    return False


def approve_page(resource, entry):
    """Record the current version of the page a resource is posted on."""
    page_url = resource["page"]
    final_url, ctype, body = fetch(page_url)
    _, digest, text = fingerprint(ctype, body)
    entry.update({
        "page_url": page_url,
        "page_hash": digest,
        "page_links": links_to(body, final_url, resource["url"]),
        "page_status": "ok",
        "page_fail_count": 0,
    })
    entry.pop("pending_page_hash", None)
    if text is not None:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        (SNAPSHOT_DIR / f"{resource['id']}--page.txt").write_text(text, encoding="utf-8")
    return entry


def copy_path(rid):
    return FILES_DIR / f"{rid}.pdf"


def approve(resource, status, keep_copy=False):
    """Fetch the resource now and record the current version as approved."""
    final_url, ctype, body = fetch(resource["url"])
    kind, digest, text = fingerprint(ctype, body)
    rid = resource["id"]
    entry = {
        "url": resource["url"],
        "kind": kind,
        "approved_hash": digest,
        "approved_at": now(),
        "last_checked": now(),
        "status": "ok",
        "fail_count": 0,
        "message": "",
    }
    if kind == "pdf":
        path = copy_path(rid)
        if not (keep_copy and path.exists()):
            FILES_DIR.mkdir(exist_ok=True)
            path.write_bytes(body)
        entry["copy"] = path.relative_to(ROOT).as_posix()
    elif text is not None:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        (SNAPSHOT_DIR / f"{rid}.txt").write_text(text, encoding="utf-8")
    if resource.get("page"):
        approve_page(resource, entry)
    status[rid] = entry
    return entry
