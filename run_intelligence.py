#!/usr/bin/env python3
"""
ARTHA — Standalone Intelligence Runner
Reads pain_signals.csv directly. No database required.
Runs: embeddings → clustering → evidence packs → ranked signal report.

Usage:
  python run_intelligence.py
  python run_intelligence.py --min-cluster 3 --top 10
  python run_intelligence.py --save report.json

Requirements (install once):
  pip install sentence-transformers scikit-learn hdbscan
"""

import csv
import json
import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter

DATA_FILE = Path(__file__).parent / "data" / "pain_signals.csv"

# ── Minimal Post object (mirrors storage/models.py) ─────────────────────────

@dataclass
class Post:
    id: str
    source: str = "reddit"
    community: str = ""
    thread_id: str = ""
    title: str = ""
    body: str = ""
    url: str = ""
    engagement: int = 0
    comment_count: int = 0
    signal_score: int = 1
    matched_keywords: str = ""


def load_posts(path: Path) -> list[Post]:
    posts = []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            posts.append(Post(
                id=f"reddit:{row.get('post_id', i)}",
                community=row.get("subreddit", ""),
                thread_id=row.get("post_id", str(i)),
                title=row.get("title", ""),
                body=row.get("body_preview", ""),
                url=row.get("url", ""),
                engagement=int(row.get("upvotes", 0) or 0),
                comment_count=int(row.get("comments", 0) or 0),
                signal_score=int(row.get("score", 1) or 1),
                matched_keywords=row.get("matched_keyword", ""),
            ))
    return posts


# ── Embeddings ───────────────────────────────────────────────────────────────

def embed_posts(posts: list[Post]):
    from sentence_transformers import SentenceTransformer
    import numpy as np

    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [f"{p.title} {p.body}"[:512].strip() for p in posts]
    print(f"  Embedding {len(texts)} posts…")
    vecs = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    return vecs


# ── Clustering ───────────────────────────────────────────────────────────────

def cluster_posts(embeddings, posts: list[Post], min_cluster_size: int = 4) -> dict[int, list[Post]]:
    import numpy as np
    from collections import defaultdict

    try:
        import hdbscan
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=2,
                                     metric="euclidean", cluster_selection_method="eom")
        labels = clusterer.fit_predict(embeddings)
    except ImportError:
        from sklearn.cluster import DBSCAN
        clusterer = DBSCAN(eps=0.4, min_samples=2, metric="cosine")
        labels = clusterer.fit_predict(embeddings)

    clusters = defaultdict(list)
    for post, label in zip(posts, labels):
        clusters[int(label)].append(post)

    # reassign noise to nearest cluster
    from sklearn.metrics.pairwise import cosine_similarity
    noise = clusters.pop(-1, [])
    if noise and clusters:
        cids = list(clusters.keys())
        centroids = np.array([
            embeddings[[i for i, p in enumerate(posts) if p in clusters[cid]]].mean(axis=0)
            for cid in cids
        ])
        noise_vecs = embeddings[[i for i, p in enumerate(posts) if p in noise]]
        sims = cosine_similarity(noise_vecs, centroids)
        for post, sim_row in zip(noise, sims):
            clusters[cids[sim_row.argmax()]].append(post)

    return dict(clusters)


def label_cluster(posts: list[Post]) -> str:
    from sklearn.feature_extraction.text import TfidfVectorizer
    texts = [f"{p.title} {p.body[:200]}".strip() for p in posts if p.title]
    if not texts:
        return "unknown"
    try:
        tfidf = TfidfVectorizer(max_features=500, stop_words="english",
                                ngram_range=(1, 2), min_df=1)
        tfidf.fit_transform(texts)
        scores = sorted(zip(tfidf.get_feature_names_out(), tfidf.idf_), key=lambda x: x[1])
        return " · ".join(t for t, _ in scores[:3])
    except Exception:
        return "mixed"


# ── Evidence Pack ─────────────────────────────────────────────────────────────

def build_pack(cluster_id: int, posts: list[Post]) -> dict:
    avg_score = sum(p.signal_score for p in posts) / len(posts)
    avg_engagement = sum(p.engagement for p in posts) / len(posts)
    communities = sorted(set(p.community for p in posts))
    keywords = Counter(kw.strip() for p in posts
                       for kw in p.matched_keywords.split(",") if kw.strip())

    # top quotes = highest engagement posts, title as quote
    top_posts = sorted(posts, key=lambda p: p.engagement, reverse=True)[:3]
    top_quotes = [{"text": p.title, "url": p.url, "upvotes": p.engagement} for p in top_posts]

    return {
        "cluster_id":    cluster_id,
        "label":         label_cluster(posts),
        "frequency":     len(posts),
        "avg_score":     round(avg_score, 2),
        "avg_engagement": round(avg_engagement, 1),
        "communities":   communities,
        "top_keywords":  [kw for kw, _ in keywords.most_common(5)],
        "top_quotes":    top_quotes,
    }


# ── Report ────────────────────────────────────────────────────────────────────

def print_report(packs: list[dict], top: int) -> None:
    BOLD = "\033[1m"; RESET = "\033[0m"; GREEN = "\033[92m"; YEL = "\033[93m"

    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  ARTHA INTELLIGENCE REPORT — top {min(top, len(packs))} clusters{RESET}")
    print(f"  Total clusters found: {len(packs)}")
    print(f"{BOLD}{'='*70}{RESET}\n")

    for i, pack in enumerate(packs[:top], 1):
        score_color = GREEN if pack["avg_score"] >= 2.5 else YEL
        print(f"{BOLD}#{i}  {pack['label'].upper()}{RESET}")
        print(f"    Posts: {pack['frequency']}  |  "
              f"Avg score: {score_color}{pack['avg_score']}{RESET}  |  "
              f"Avg upvotes: {pack['avg_engagement']:.0f}")
        print(f"    Communities: {', '.join(pack['communities'])}")
        print(f"    Keywords: {', '.join(pack['top_keywords'])}")
        print(f"    Top signals:")
        for q in pack["top_quotes"]:
            print(f"      [{q['upvotes']}↑] {q['text'][:90]}")
            print(f"             {q['url']}")
        print()

    print(f"{BOLD}{'='*70}{RESET}")
    print(f"\n{BOLD}Potential new signals (freq ≥ 5, avg_score ≥ 2.0):{RESET}")
    candidates = [p for p in packs if p["frequency"] >= 5 and p["avg_score"] >= 2.0]
    if candidates:
        for p in candidates:
            print(f"  • {p['label']}  ({p['frequency']} posts, score {p['avg_score']})")
    else:
        print("  None meeting threshold yet — run digest again in 2 days.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Run ARTHA intelligence pipeline on pain_signals.csv")
    parser.add_argument("--min-cluster", type=int, default=4, help="Min posts per cluster (default: 4)")
    parser.add_argument("--top", type=int, default=10, help="Top N clusters to show (default: 10)")
    parser.add_argument("--save", metavar="FILE", help="Save full report as JSON")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading signals from {DATA_FILE}…")
    posts = load_posts(DATA_FILE)
    print(f"  {len(posts)} posts loaded.\n")

    embeddings = embed_posts(posts)

    print(f"\nClustering (min_cluster_size={args.min_cluster})…")
    clusters = cluster_posts(embeddings, posts, min_cluster_size=args.min_cluster)
    print(f"  {len(clusters)} clusters found.\n")

    print("Building evidence packs…")
    packs = [build_pack(cid, cluster_posts_list)
             for cid, cluster_posts_list in clusters.items()]
    packs.sort(key=lambda p: (p["avg_score"], p["frequency"]), reverse=True)

    print_report(packs, top=args.top)

    if args.save:
        Path(args.save).write_text(json.dumps(packs, indent=2))
        print(f"Full report saved to {args.save}")


if __name__ == "__main__":
    main()
