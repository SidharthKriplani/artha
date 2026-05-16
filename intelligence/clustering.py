"""
ARTHA — Clustering Module
HDBSCAN over post embeddings + TF-IDF cluster label generation.

Why HDBSCAN over K-means:
- No fixed k required — cluster count is data-driven
- Handles noise naturally (posts that don't fit any cluster get label -1)
- Works well with varying cluster densities (some pain themes are niche, some are widespread)
"""

import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    from sklearn.cluster import DBSCAN


def cluster_posts(embeddings: np.ndarray, posts: list,
                  min_cluster_size: int = 4,
                  min_samples: int = 2) -> dict[int, list]:
    """
    Cluster posts by embedding similarity.
    Returns dict: {cluster_id: [post, ...]}
    Noise cluster is stored under key -1.
    """
    if len(posts) < min_cluster_size:
        return {0: posts}

    if HDBSCAN_AVAILABLE:
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",
            cluster_selection_method="eom"
        )
        labels = clusterer.fit_predict(embeddings)
    else:
        # Fallback: DBSCAN
        clusterer = DBSCAN(eps=0.4, min_samples=min_samples, metric="cosine")
        labels = clusterer.fit_predict(embeddings)

    clusters = defaultdict(list)
    for post, label in zip(posts, labels):
        clusters[int(label)].append(post)

    # Reassign noise posts to nearest non-noise cluster centroid
    noise_posts = clusters.pop(-1, [])
    if noise_posts and clusters:
        cluster_ids   = list(clusters.keys())
        centroids     = np.array([
            embeddings[[i for i, p in enumerate(posts)
                        if p in clusters[cid]]].mean(axis=0)
            for cid in cluster_ids
        ])
        noise_indices = [i for i, p in enumerate(posts) if p in noise_posts]
        noise_vecs    = embeddings[noise_indices]
        sims          = cosine_similarity(noise_vecs, centroids)
        for post, sim_row in zip(noise_posts, sims):
            nearest_cid = cluster_ids[sim_row.argmax()]
            clusters[nearest_cid].append(post)

    return dict(clusters)


def label_cluster(posts: list, top_n: int = 3) -> str:
    """
    Generate a human-readable cluster label using TF-IDF on post titles.
    Returns top N terms joined as a string.
    """
    texts = [(p.title or "") + " " + (p.body or "")[:200] for p in posts]
    texts = [t.strip() for t in texts if t.strip()]

    if not texts:
        return "unknown"

    try:
        tfidf = TfidfVectorizer(
            max_features=500,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1
        )
        tfidf.fit_transform(texts)
        scores   = zip(tfidf.get_feature_names_out(),
                       tfidf.idf_)
        sorted_  = sorted(scores, key=lambda x: x[1])          # lower idf = more distinctive
        top_terms = [term for term, _ in sorted_[:top_n]]
        return " · ".join(top_terms)
    except Exception:
        return "mixed signals"


def get_cluster_communities(posts: list) -> list[str]:
    """Return sorted unique list of communities contributing to this cluster."""
    return sorted(set(p.community for p in posts if p.community))
