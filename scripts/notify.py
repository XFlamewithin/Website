"""Send link-check notifications.

Two channels, each used only if configured:
  * Email over SMTP — set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD and
    NOTIFY_EMAIL (e.g. as GitHub repository secrets).
  * A GitHub issue per resource — automatic when running in GitHub Actions
    (GITHUB_TOKEN and GITHUB_REPOSITORY). GitHub emails the repository owner
    about new issues, so this works even without SMTP.
"""

import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage

from common import load_site

HEADINGS = {
    "changed": "Content has changed",
    "broken": "Link appears to be broken (page or file not found)",
    "unreachable": "Could not be checked for several days (still shown on the website)",
}


def describe(kind, r, entry, detail):
    lines = [
        f"{HEADINGS[kind]}: {r['title']}",
        "",
        f"Resource id: {r['id']}",
        f"Link:        {r['url']}",
        f"Approved:    {entry.get('approved_at', 'never')}",
        f"Detected:    {entry.get('last_checked')}",
    ]
    if kind in ("changed", "broken"):
        if entry.get("kind") == "pdf":
            lines += ["", "Your website now links only to your saved (approved) copy of this PDF."]
        else:
            lines += ["", "This link is hidden from your website until you approve it again."]
    if detail:
        lines += ["", "What changed:", detail]
    lines += [
        "",
        "To approve the current version:",
        "  GitHub → Actions → 'Check links & publish' → Run workflow →",
        f"  action: approve, resource id: {r['id']}",
        "  (choose 'keep saved copy' if you want to keep your old PDF copy).",
        "",
        "Or edit the url in resources.toml if you want to point to a different resource.",
    ]
    return "\n".join(lines)


def send_email(events, bodies):
    host = os.environ.get("SMTP_HOST")
    to = os.environ.get("NOTIFY_EMAIL")
    if not (host and to):
        return
    site = load_site()
    msg = EmailMessage()
    names = ", ".join(r["title"] for _, r, _, _ in events)
    msg["Subject"] = f"[{site['name']} website] Please review: {names}"[:200]
    msg["From"] = os.environ.get("SMTP_FROM") or os.environ.get("SMTP_USER") or to
    msg["To"] = to
    msg.set_content(("\n\n" + "=" * 60 + "\n\n").join(bodies))
    port = int(os.environ.get("SMTP_PORT") or 587)
    with smtplib.SMTP_SSL(host, port) if port == 465 else smtplib.SMTP(host, port) as s:
        if port != 465:
            s.starttls()
        if os.environ.get("SMTP_USER"):
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        s.send_message(msg)
    print(f"Email sent to {to}")


def create_issues(events, bodies):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not (token and repo):
        return
    for (kind, r, _, _), body in zip(events, bodies):
        title = f"[Link check] {kind.capitalize()}: {r['title']} ({r['id']})"
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/issues",
            data=json.dumps({"title": title, "body": f"```\n{body}\n```"}).encode(),
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            print(f"Opened issue: {json.load(resp)['html_url']}")


def close_issues(rid):
    """Close open link-check issues for a resource after it is approved."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not (token and repo):
        return
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100",
                                 headers=headers)
    with urllib.request.urlopen(req) as resp:
        issues = json.load(resp)
    for issue in issues:
        if issue["title"].startswith("[Link check]") and issue["title"].endswith(f"({rid})"):
            urllib.request.urlopen(urllib.request.Request(
                issue["url"], data=json.dumps({"state": "closed"}).encode(),
                headers=headers, method="PATCH"))
            print(f"Closed issue #{issue['number']}")


def send(events):
    bodies = [describe(*e) for e in events]
    for channel in (send_email, create_issues):
        try:
            channel(events, bodies)
        except Exception as e:  # never let a notification problem stop the site update
            print(f"Notification via {channel.__name__} failed: {e}")
    if not (os.environ.get("SMTP_HOST") or os.environ.get("GITHUB_TOKEN")):
        print("(No email or GitHub settings found — printing instead.)\n")
        print("\n\n".join(bodies))
