"""Daily link check.

For every resource in resources.toml:
  * new resources (or ones whose url was edited) are fetched and approved
    automatically, and a saved copy of any PDF is stored in files/;
  * existing resources are compared with the approved version. If the content
    changed, or the link is gone, the resource is paused on the website and a
    notification is sent (email and/or GitHub issue) asking for re-approval.

Run locally with:  python3 scripts/check_links.py
"""

import sys

from common import (PAUSED, SNAPSHOT_DIR, FetchError, approve, fetch, fingerprint,
                    load_resources, load_status, now, save_status, text_diff)
import notify

BROKEN_AFTER = 2       # a 404 / unknown host must repeat on this many daily checks
UNREACHABLE_AFTER = 3  # other errors (blocked, timeouts, server errors) before we warn


def check_one(r, status, events):
    rid = r["id"]
    entry = status.get(rid)

    if r["check"] == "off":
        status[rid] = {"url": r["url"], "status": "unchecked", "message": "Automatic checking is off"}
        return

    if entry is None or entry.get("url") != r["url"] or "approved_hash" not in entry:
        try:
            approve(r, status)
            print(f"  NEW      {rid}: approved current version")
        except FetchError as e:
            status[rid] = {"url": r["url"], "status": "unchecked", "fail_count": 0,
                           "message": f"Could not fetch when first added: {e}", "last_checked": now()}
            print(f"  NEW      {rid}: could not fetch ({e}) — will retry tomorrow")
        return

    entry["last_checked"] = now()
    try:
        _, ctype, body = fetch(r["url"])
    except FetchError as e:
        entry["fail_count"] = entry.get("fail_count", 0) + 1
        print(f"  ERROR    {rid}: {e} (attempt {entry['fail_count']})")
        if entry["status"] in PAUSED or entry["status"] == "unreachable":
            return
        if e.permanent and entry["fail_count"] >= BROKEN_AFTER:
            entry["status"] = "broken"
            entry["message"] = str(e)
            events.append(("broken", r, entry, str(e)))
        elif not e.permanent and entry["fail_count"] >= UNREACHABLE_AFTER:
            entry["status"] = "unreachable"
            entry["message"] = str(e)
            events.append(("unreachable", r, entry, str(e)))
        return

    entry["fail_count"] = 0
    kind, digest, text = fingerprint(ctype, body)
    if digest == entry["approved_hash"]:
        # Unchanged — or, if it was paused, it has gone back to the approved version.
        print(f"  OK       {rid}")
        entry["status"], entry["message"] = "ok", ""
        entry.pop("pending_hash", None)
        return

    if entry.get("pending_hash") == digest:
        print(f"  CHANGED  {rid}: still awaiting approval")
        return  # already notified about this exact version

    entry["status"] = "changed"
    entry["pending_hash"] = digest
    entry["message"] = f"Content changed (detected {now()})"
    detail = ""
    if kind != entry.get("kind"):
        detail = f"The link used to be a {entry.get('kind')} and is now a {kind}."
    elif kind == "page" and text is not None:
        snap = SNAPSHOT_DIR / f"{rid}.txt"
        if snap.exists():
            detail = text_diff(snap.read_text(encoding="utf-8"), text)
    print(f"  CHANGED  {rid}")
    events.append(("changed", r, entry, detail))


def main():
    resources = load_resources()
    status = load_status()
    events = []
    print(f"Checking {len(resources)} resources…")
    for r in resources:
        check_one(r, status, events)
    # Forget resources that were removed from resources.toml.
    ids = {r["id"] for r in resources}
    for rid in list(status):
        if rid not in ids:
            del status[rid]
    save_status(status)

    if events:
        print(f"\n{len(events)} resource(s) need attention — sending notifications.")
        notify.send(events)
    else:
        print("\nAll resources OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
