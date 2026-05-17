"""
artha-ai.sig — Evidence Pack Generator
Converts a cluster of posts into a structured evidence pack.
Output is a dict ready to display in UI or export as JSON.

Design principle: present evidence, never render verdicts.
The founder reads the evidence and decides. artha-ai.sig does not say "build this."
"""

import uuid
from datetime import datetime
from intelligence.clustering import label_cluster, get_cluster_communities
from intelligence.scoring import (
    rank_quotes, extract_workarounds, extract_tool_rejections,
    infer_persona, cluster_intensity, evidence_quality
)


def build_evidence_pack(cluster_id: int, posts: list, scan_id: str = None) -> dict:
    """
    Build a full evidence pack for one pain cluster.
    """
    if not posts:
        return {}

    label        = label_cluster(posts)
    top_quotes   = rank_quotes(posts, top_n=5)
    workarounds  = extract_workarounds(posts)
    rejections   = extract_tool_rejections(posts)
    persona      = infer_persona(posts)
    intensity    = cluster_intensity(posts)
    eq           = evidence_quality(top_quotes)
    communities  = get_cluster_communities(posts)

    # Frequency trend: posts per community
    community_dist = {}
    for post in posts:
        community_dist[post.community] = community_dist.get(post.community, 0) + 1

    # Top upvoted post as signal anchor
    anchor = max(posts, key=lambda p: p.engagement or 0)

    return {
        "cluster_id":      cluster_id,
        "scan_id":         scan_id or str(uuid.uuid4()),
        "generated_at":    datetime.utcnow().isoformat(),

        # Core signal
        "label":           label,
        "frequency":       len(posts),
        "intensity_score": intensity,
        "evidence_quality":eq,
        "communities":     communities,
        "community_dist":  community_dist,
        "detected_persona":persona,

        # Anchor post (highest engagement)
        "anchor": {
            "title":    anchor.title,
            "url":      anchor.url,
            "upvotes":  anchor.engagement,
            "comments": anchor.comment_count,
        },

        # Evidence sections
        "top_quotes": [
            {"text": q.text, "url": q.url, "score": q.score}
            for q in top_quotes
        ],
        "workaround_patterns": [
            {"text": w.text, "url": w.url}
            for w in workarounds
        ],
        "tool_rejections": [
            {"tool": r.tool, "reason": r.reason_snippet, "url": r.url}
            for r in rejections
        ],

        # Where to find these people
        "reachable_communities": [
            f"r/{c}" if not c.startswith("r/") else c
            for c in communities
        ],
    }


def build_scan_report(clusters: dict[int, list], scan_id: str = None) -> dict:
    """
    Build a full scan report from all clusters.
    Sorted by intensity × frequency (strongest signals first).
    """
    scan_id   = scan_id or str(uuid.uuid4())
    packs     = []

    for cluster_id, posts in clusters.items():
        if len(posts) < 2:
            continue
        pack = build_evidence_pack(cluster_id, posts, scan_id)
        if pack:
            packs.append(pack)

    # Sort: high intensity + high frequency first
    packs.sort(
        key=lambda p: p["intensity_score"] * 0.6 + min(p["frequency"] / 20, 1.0) * 0.4,
        reverse=True
    )

    return {
        "scan_id":      scan_id,
        "generated_at": datetime.utcnow().isoformat(),
        "total_posts":  sum(len(posts) for posts in clusters.values()),
        "total_clusters": len(packs),
        "evidence_packs": packs,
    }
