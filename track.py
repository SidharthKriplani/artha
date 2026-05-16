"""
ARTHA Signal Tracker
Append-only lifecycle manager for pain signals.

Usage:
  python3 track.py --list
  python3 track.py --claim SIGNAL-002 --github your-username
  python3 track.py --update SIGNAL-002 --status building
  python3 track.py --update SIGNAL-002 --status deployed --solution my-solution-folder
  python3 track.py --add --id <reddit_id> --ref SIGNAL-008 --notes "description"

Statuses: open → claimed → building → deployed → parked → superseded
"""

import csv
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

TRACKER_FILE = Path(__file__).parent / "data" / "signal_tracker.csv"
COLUMNS = ["signal_id", "signal_ref", "status", "claimed_by",
           "solution_ref", "notes", "timestamp"]

VALID_STATUSES = ["open", "claimed", "building", "deployed", "parked", "superseded"]


def load() -> list[dict]:
    if not TRACKER_FILE.exists():
        return []
    with open(TRACKER_FILE) as f:
        return list(csv.DictReader(f))


def append_row(row: dict):
    """Append a single row to the tracker. Never modifies existing rows."""
    file_exists = TRACKER_FILE.exists()
    with open(TRACKER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def get_latest(rows: list[dict], signal_ref: str) -> dict | None:
    """Get the most recent row for a signal_ref."""
    matches = [r for r in rows if r["signal_ref"] == signal_ref]
    return matches[-1] if matches else None


def cmd_list(args):
    rows = load()
    # Show latest state per signal
    seen = {}
    for r in rows:
        seen[r["signal_ref"]] = r  # last entry wins

    if not seen:
        print("No signals tracked yet.")
        return

    STATUS_ICONS = {
        "open": "🔴", "claimed": "🟡", "building": "🟠",
        "deployed": "✅", "parked": "⏸️", "superseded": "⬛"
    }

    print(f"\n{'Ref':<14} {'Status':<12} {'Claimed By':<22} {'Solution':<25} {'Notes'}")
    print("-" * 100)
    for ref, r in sorted(seen.items()):
        icon = STATUS_ICONS.get(r["status"], "❓")
        print(f"{r['signal_ref']:<14} {icon} {r['status']:<10} "
              f"{r['claimed_by'] or '-':<22} "
              f"{r['solution_ref'] or '-':<25} "
              f"{r['notes'][:50] if r['notes'] else ''}")
    print()


def cmd_claim(args):
    rows = load()
    latest = get_latest(rows, args.claim)
    if not latest:
        print(f"Signal {args.claim} not found in tracker.")
        sys.exit(1)
    if latest["status"] not in ("open",):
        print(f"Signal {args.claim} is already {latest['status']} — cannot claim.")
        sys.exit(1)

    new_row = {**latest,
               "status": "claimed",
               "claimed_by": args.github,
               "timestamp": now()}
    append_row(new_row)
    print(f"✓ {args.claim} claimed by @{args.github}")


def cmd_update(args):
    rows = load()
    latest = get_latest(rows, args.update)
    if not latest:
        print(f"Signal {args.update} not found.")
        sys.exit(1)
    if args.status not in VALID_STATUSES:
        print(f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}")
        sys.exit(1)

    new_row = {**latest,
               "status": args.status,
               "timestamp": now()}
    if args.solution:
        new_row["solution_ref"] = args.solution
    if args.notes:
        new_row["notes"] = args.notes

    append_row(new_row)
    print(f"✓ {args.update} → {args.status}")


def cmd_add(args):
    row = {
        "signal_id":  args.id,
        "signal_ref": args.ref,
        "status":     "open",
        "claimed_by": "",
        "solution_ref": "",
        "notes":      args.notes or "",
        "timestamp":  now(),
    }
    append_row(row)
    print(f"✓ Added {args.ref} (reddit id: {args.id})")


def main():
    parser = argparse.ArgumentParser(description="ARTHA Signal Tracker")
    parser.add_argument("--list",   action="store_true", help="List all signals")
    parser.add_argument("--claim",  metavar="SIGNAL_REF", help="Claim a signal")
    parser.add_argument("--github", metavar="USERNAME",   help="Your GitHub username (for --claim)")
    parser.add_argument("--update", metavar="SIGNAL_REF", help="Update a signal")
    parser.add_argument("--status", metavar="STATUS",     help="New status")
    parser.add_argument("--solution", metavar="FOLDER",   help="Solution folder name")
    parser.add_argument("--notes",  metavar="TEXT",       help="Notes")
    parser.add_argument("--add",    action="store_true",  help="Add a new signal")
    parser.add_argument("--id",     metavar="REDDIT_ID",  help="Reddit post ID")
    parser.add_argument("--ref",    metavar="SIGNAL_REF", help="Signal ref (e.g. SIGNAL-008)")

    args = parser.parse_args()

    if args.list:
        cmd_list(args)
    elif args.claim:
        if not args.github:
            print("--github required with --claim")
            sys.exit(1)
        cmd_claim(args)
    elif args.update:
        if not args.status:
            print("--status required with --update")
            sys.exit(1)
        cmd_update(args)
    elif args.add:
        if not args.id or not args.ref:
            print("--id and --ref required with --add")
            sys.exit(1)
        cmd_add(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
