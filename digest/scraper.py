"""
artha-ai.sig v0 — Reddit Pain Point Digest
Scrapes public subreddits for AI/ML builder pain signals.
No API key required. Uses Reddit's public JSON endpoint.
"""

import csv
import json
import os
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Configuration ─────────────────────────────────────────────────────────────

SUBREDDITS = [
    # Global AI/ML builder communities
    "LocalLLaMA",
    "MachineLearning",
    "LanguageModelHacking",
    "SideProject",
    "devtools",
    # Indian tech / startup communities
    "developersIndia",
    "indianstartups",
]

PAIN_KEYWORDS = [
    # Frustration signals
    "stuck", "frustrated", "annoying", "impossible", "broken",
    "doesn't work", "does not work", "won't work", "not working",
    "no way to", "can't figure out", "cannot figure out",
    # Workaround signals
    "workaround", "hack around", "manually", "switched from", "gave up",
    "wish there was", "wish it had", "would be nice if",
    # Gap signals
    "no library", "no tool", "no good way", "nothing exists",
    "why is there no", "why doesn't", "why can't",
    # AI/ML specific pain
    "hallucinating", "hallucination", "context window", "token limit",
    "evaluation", "eval", "rag pipeline", "chunking", "embedding",
    "agent loop", "tool call", "function calling", "memory",
    "latency", "cost too high", "rate limit", "prompt leaking",
    "fine tuning", "fine-tuning", "finetuning", "inference speed",
    "deployment", "observability", "tracing", "debugging agent",
]

POSTS_PER_SUBREDDIT = 100
OUTPUT_DIR = Path(__file__).parent.parent / "data"
SEEN_IDS_FILE = OUTPUT_DIR / "seen_ids.json"
CSV_FILE = OUTPUT_DIR / "pain_signals.csv"

HEADERS = {
    "User-Agent": "artha-v0/0.1 pain-point-digest (personal research tool)"
}

CSV_COLUMNS = [
    "id", "date", "subreddit", "title", "url",
    "upvotes", "comments", "matched_keywords",
    "keyword_count", "score", "body_snippet"
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_seen_ids() -> set:
    if SEEN_IDS_FILE.exists():
        with open(SEEN_IDS_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_ids(seen: set):
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(list(seen), f)


def score_post(upvotes: int, comments: int, keyword_count: int) -> int:
    """
    Simple 1–3 signal strength score.
    3 = high priority, 2 = worth reviewing, 1 = weak signal
    """
    points = 0
    if upvotes >= 50:
        points += 1
    if upvotes >= 200:
        points += 1
    if comments >= 10:
        points += 1
    if comments >= 30:
        points += 1
    if keyword_count >= 2:
        points += 1
    if keyword_count >= 4:
        points += 1

    if points >= 4:
        return 3
    elif points >= 2:
        return 2
    else:
        return 1


def find_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in PAIN_KEYWORDS if kw in text_lower]


def fetch_posts(subreddit: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={POSTS_PER_SUBREDDIT}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("children", [])
    except Exception as e:
        print(f"  [!] Failed to fetch r/{subreddit}: {e}")
        return []


def snippet(text: str, max_chars: int = 200) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    return text[:max_chars] + "..." if len(text) > max_chars else text


# ── Main ──────────────────────────────────────────────────────────────────────

def run(no_push: bool = False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seen_ids = load_seen_ids()

    # Load existing CSV rows to append
    file_exists = CSV_FILE.exists()
    new_rows = []

    print(f"\n{'='*55}")
    print(f"  artha-ai.sig v0 — Pain Signal Digest")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*55}\n")

    for subreddit in SUBREDDITS:
        print(f"Scanning r/{subreddit}...")
        posts = fetch_posts(subreddit)
        found = 0

        for post in posts:
            p = post.get("data", {})
            post_id = p.get("id", "")

            if post_id in seen_ids:
                continue

            title = p.get("title", "")
            body = p.get("selftext", "")
            combined = f"{title} {body}"

            matched = find_keywords(combined)
            if not matched:
                seen_ids.add(post_id)
                continue

            upvotes = p.get("ups", 0)
            comments = p.get("num_comments", 0)
            keyword_count = len(matched)
            signal_score = score_post(upvotes, comments, keyword_count)
            post_url = "https://reddit.com" + p.get("permalink", "")
            created = datetime.fromtimestamp(
                p.get("created_utc", 0), tz=timezone.utc
            ).strftime("%Y-%m-%d")

            row = {
                "id": post_id,
                "date": created,
                "subreddit": subreddit,
                "title": title,
                "url": post_url,
                "upvotes": upvotes,
                "comments": comments,
                "matched_keywords": " | ".join(matched),
                "keyword_count": keyword_count,
                "score": signal_score,
                "body_snippet": snippet(body),
            }

            new_rows.append(row)
            seen_ids.add(post_id)
            found += 1

        print(f"  → {found} new pain signals found")
        time.sleep(2)  # polite delay between subreddit requests

    # Write to CSV
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_rows)

    save_seen_ids(seen_ids)

    print(f"\n{'='*55}")
    print(f"  Total new signals: {len(new_rows)}")
    print(f"  Saved to: {CSV_FILE}")
    print(f"{'='*55}\n")

    # Print top signals (score = 3) to terminal
    top = [r for r in new_rows if r["score"] == 3]
    if top:
        print(f"  TOP SIGNALS (score 3/3):\n")
        for r in top[:5]:
            print(f"  [{r['subreddit']}] {r['title'][:80]}")
            print(f"  {r['url']}")
            print(f"  Upvotes: {r['upvotes']} | Comments: {r['comments']} | Keywords: {r['matched_keywords'][:60]}")
            print()

    # Auto-push new signals to GitHub (skipped in CI — workflow handles it)
    if new_rows and not no_push:
        _autopush(len(new_rows))


def _autopush(new_count: int):
    """Commit and push updated pain_signals.csv to GitHub automatically."""
    import subprocess

    repo_root = Path(__file__).parent.parent
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    commands = [
        ["git", "-C", str(repo_root), "add", "data/pain_signals.csv"],
        ["git", "-C", str(repo_root), "commit", "-m",
         f"data: +{new_count} pain signals [{timestamp}]"],
        ["git", "-C", str(repo_root), "push"],
    ]

    print("  Pushing signals to GitHub...")
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # commit fails cleanly if nothing changed — not an error
            if "nothing to commit" in result.stdout + result.stderr:
                print("  Nothing new to push.")
                return
            print(f"  Git warning: {result.stderr.strip()}")
            return

    print(f"  ✓ Pushed {new_count} new signals to GitHub.\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-push", action="store_true",
                        help="Skip auto-push to GitHub (used by CI)")
    args = parser.parse_args()
    run(no_push=args.no_push)
