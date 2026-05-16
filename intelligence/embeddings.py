"""
ARTHA — Embeddings Pipeline
Converts post text into dense vectors using sentence-transformers.
Embeddings are cached to disk to avoid recomputing on repeat runs.
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from typing import List

from sentence_transformers import SentenceTransformer

MODEL_NAME  = "all-MiniLM-L6-v2"
CACHE_DIR   = Path(__file__).parent.parent / "data" / "embedding_cache"
MAX_CHARS   = 512

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"  Loading embedding model: {MODEL_NAME}...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def make_text(post) -> str:
    """Combine title + body into one embedding input string."""
    title = (post.title or "").strip()
    body  = (post.body  or "").strip()
    combined = f"{title} {body}".strip()
    return combined[:MAX_CHARS]


def cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def load_cache() -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "embeddings.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    cache_file = CACHE_DIR / "embeddings.json"
    with open(cache_file, "w") as f:
        json.dump(cache, f)


def generate_embeddings(posts: list) -> np.ndarray:
    """
    Generate embeddings for a list of Post objects.
    Uses disk cache — already-seen texts are not recomputed.
    Returns numpy array of shape (n_posts, embedding_dim).
    """
    model  = get_model()
    cache  = load_cache()
    texts  = [make_text(p) for p in posts]

    # Separate cached vs. new
    new_indices = [i for i, t in enumerate(texts) if cache_key(t) not in cache]
    new_texts   = [texts[i] for i in new_indices]

    if new_texts:
        print(f"  Embedding {len(new_texts)} new posts (cached: {len(texts) - len(new_texts)})...")
        new_vecs = model.encode(new_texts, batch_size=64,
                                show_progress_bar=len(new_texts) > 100,
                                normalize_embeddings=True)
        for idx, vec in zip(new_indices, new_vecs):
            cache[cache_key(texts[idx])] = vec.tolist()
        save_cache(cache)
    else:
        print(f"  All {len(texts)} embeddings loaded from cache.")

    # Reconstruct in original order
    matrix = np.array([cache[cache_key(t)] for t in texts], dtype=np.float32)
    return matrix
