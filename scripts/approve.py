"""Approve the current version of a resource after reviewing a change.

    python3 scripts/approve.py <resource-id>              # approve and update the saved PDF copy
    python3 scripts/approve.py <resource-id> --keep-copy  # approve but keep the old saved PDF
    python3 scripts/approve.py --all-pending              # approve everything awaiting review
"""

import argparse
import sys

from common import PAUSED, approve, effective_status, load_resources, load_status, save_status
import notify


def main():
    p = argparse.ArgumentParser()
    p.add_argument("id", nargs="?", help="resource id (shown in the notification)")
    p.add_argument("--keep-copy", action="store_true", help="keep the existing saved PDF copy")
    p.add_argument("--all-pending", action="store_true", help="approve all paused resources")
    args = p.parse_args()

    resources = {r["id"]: r for r in load_resources()}
    status = load_status()
    if args.all_pending:
        ids = [rid for rid, e in status.items()
               if effective_status(e) in PAUSED | {"withdrawn"} and rid in resources]
    elif args.id:
        if args.id not in resources:
            sys.exit(f"No resource with id '{args.id}'. Ids: {', '.join(resources)}")
        ids = [args.id]
    else:
        p.error("give a resource id or --all-pending")

    for rid in ids:
        approve(resources[rid], status, keep_copy=args.keep_copy)
        save_status(status)
        print(f"Approved {rid}" + (" (kept old saved copy)" if args.keep_copy else ""))
        notify.close_issues(rid)
    if not ids:
        print("Nothing awaiting approval.")


if __name__ == "__main__":
    main()
