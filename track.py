"""
ARTHA Signal Tracker
Append-only lifecycle manager for pain signals.

Usage:
  python3 track.py --list
  python3 track.py --claim SIGNAL-002 --github your-username
  python3 track.py --update SIGNAL-002 --status building
  python3 track.py --update SIGNAL-002 --status deployed --solution my-solution-folder
  python3 track.py --add --id <reddit_id> --ref SIGNAL-008 --notes "description"
  python3 track.py --expire SIGNAL-002   ← maintainer: free a stale claim manually

Statuses: open → claimed → building → deployed → parked → superseded

Claim expiry:
  A claimed or building signal that has not moved to deployed within 7 days
  is automatically freed when --list is run or a new --claim is attempted.
  The original claimer's work is not deleted — the signal just becomes
  claimable again. They can re-claim if still working on it.
"""

import csv
import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

TRACKER_FILE = Path(__file__).parent / "data" / "signal_tracker.csv"
COLUMNS = ["signal_id", "signal_ref", "status", "claimed_by",
           "solution_ref", "notes", "timestamp"]

VALID_STATUSES = ["open", "claimed", "building", "deployed", "parked", "superseded"]

CLAIM_EXPIRY_DAYS = 7


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


def parse_ts(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def is_expired(row: dict) -> bool:
    """Return True if a claimed/building signal is past the expiry window."""
    if row["status"] not in ("claimed", "building"):
        return False
    ts = parse_ts(row["timestamp"])
    if ts is None:
        return False
    return (datetime.now(timezone.utc) - ts) > timedelta(days=CLAIM_EXPIRY_DAYS)


def get_latest(rows: list[dict], signal_ref: str) -> dict | None:
    """Get the most recent row for a signal_ref."""
    matches = [r for r in rows if r["signal_ref"] == signal_ref]
    return matches[-1] if matches else None


def auto_expire_stale(rows: list[dict]) -> list[str]:
    """
    For any claimed/building signal past the expiry window, append an 'open'
    row to free it. Returns list of signal_refs that were freed.
    """
    freed = []
    seen = {}
    for r in rows:
        seen[r["signal_ref"]] = r  # last entry wins

    for ref, r in seen.items():
        if is_expired(r):
            freed.append(ref)
            note = f"auto-freed after {CLAIM_EXPIRY_DAYS}d (was claimed by @{r['claimed_by']})"
            append_row({**r, "status": "open", "claimed_by": "", "notes": note, "timestamp": now()})

    return freed


def cmd_list(args):
    rows = load()

    # Auto-expire before displaying
    freed = auto_expire_stale(rows)
    if freed:
        rows = load()  # reload after mutations
        for ref in freed:
            print(f"⚠️  {ref} auto-freed — claim expired after {CLAIM_EXPIRY_DAYS} days")

    seen = {}
    for r in rows:
        seen[r["signal_ref"]] = r

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
        # Show days remaining for active claims
        expiry_note = ""
        if r["status"] in ("claimed", "building"):
            ts = parse_ts(r["timestamp"])
            if ts:
                days_left = CLAIM_EXPIRY_DAYS - (datetime.now(timezone.utc) - ts).days
                expiry_note = f" [{max(0, days_left)}d left]"
        print(f"{r['signal_ref']:<14} {icon} {r['status']:<10} "
              f"{r['claimed_by'] or '-':<22} "
              f"{r['solution_ref'] or '-':<25} "
              f"{(r['notes'][:40] if r['notes'] else '')}{expiry_note}")
    print()


def check_gap_verification(signal_ref: str) -> bool:
    """Check that SIGNALS.md has a Gap verification section for this signal."""
    signals_file = Path(__file__).parent / "SIGNALS.md"
    if not signals_file.exists():
        return False
    content = signals_file.read_text()
    lines = content.split("\n")
    in_signal = False
    for line in lines:
        if signal_ref in line and line.startswith("##"):
            in_signal = True
        if in_signal and line.startswith("## ") and signal_ref not in line:
            break
        if in_signal and "Gap verification" in line:
            return True
    return False


def cmd_claim(args):
    rows = load()

    # Auto-expire stale claims before checking
    freed = auto_expire_stale(rows)
    if freed:
        rows = load()
        for ref in freed:
            print(f"⚠️  {ref} auto-freed — claim expired after {CLAIM_EXPIRY_DAYS} days")

    latest = get_latest(rows, args.claim)
    if not latest:
        print(f"Signal {args.claim} not found in tracker.")
        sys.exit(1)
    if latest["status"] not in ("open",):
        print(f"Signal {args.claim} is already {latest['status']} — cannot claim.")
        sys.exit(1)

    # Enforce gap verification before claiming
    if not check_gap_verification(args.claim):
        print(f"\n⚠️  Cannot claim {args.claim} — gap verification is missing.")
        print(f"    SIGNALS.md must have a 'Gap verification' section for {args.claim}")
        print(f"    documenting what existing tools were found and why the gap is real.")
        print(f"\n    See CONTRIBUTING.md for the required format.")
        print(f"    Add the section to SIGNALS.md, then re-run this command.\n")
        sys.exit(1)

    new_row = {**latest,
               "status": "claimed",
               "claimed_by": args.github,
               "timestamp": now()}
    append_row(new_row)
    print(f"✓ {args.claim} claimed by @{args.github}")
    print(f"  You have {CLAIM_EXPIRY_DAYS} days to open a PR or move to 'building'.")
    print(f"  Run: python3 track.py --update {args.claim} --status building")


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

    # Remind about expiry if moving to building
    if args.status == "building":
        print(f"  Clock resets — {CLAIM_EXPIRY_DAYS} days from now to reach deployed.")


def cmd_expire(args):
    """Maintainer command: manually free a stale claim."""
    rows = load()
    latest = get_latest(rows, args.expire)
    if not latest:
        print(f"Signal {args.expire} not found.")
        sys.exit(1)
    if latest["status"] not in ("claimed", "building"):
        print(f"Signal {args.expire} is {latest['status']} — nothing to expire.")
        sys.exit(1)

    note = f"manually freed by maintainer (was claimed by @{latest['claimed_by']})"
    append_row({**latest, "status": "open", "claimed_by": "", "notes": note, "timestamp": now()})
    print(f"✓ {args.expire} freed — status reset to open")


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
    parser.add_argument("--expire", metavar="SIGNAL_REF", help="[Maintainer] Manually free a stale claim")

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
    elif args.expire:
        cmd_expire(args)
    elif args.add:
        if not args.id or not args.ref:
            print("--id and --ref required with --add")
            sys.exit(1)
        cmd_add(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
