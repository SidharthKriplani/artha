"""
artha-ai.sig — Scoring Module
Quote quality ranking, workaround extraction, tool rejection detection,
persona inference, and cluster-level signal metrics.
"""

import re
from dataclasses import dataclass, field


# ── Keyword lists ─────────────────────────────────────────────────────────────

FRUSTRATION_WORDS = [
    "stuck", "frustrated", "annoying", "impossible", "broken",
    "doesn't work", "not working", "can't figure", "cannot figure",
    "no way to", "why is there no", "why doesn't", "why can't",
    "gave up", "waste of time", "useless", "terrible", "awful"
]

WORKAROUND_PATTERNS = [
    r"i (currently |just |manually )?(use|am using|started using) (.{3,40}) (instead|as a workaround|to work around|because)",
    r"my workaround (is|was|has been)",
    r"workaround[:\s]",
    r"i (have to|had to|end up) (do|doing|manually)",
    r"instead of .{3,40}, i",
    r"switched (from|away from) (.{3,40}) because",
    r"i just .{3,40} manually",
]

TOOL_REJECTION_PATTERNS = [
    r"(tried|tested|used) (.{3,40}) (but|and) (it|they) (doesn't|don't|didn't|won't|can't)",
    r"(tried|used) (.{3,40}) (and it|but it) (failed|broke|crashed|doesn't work|is too slow|is too expensive)",
    r"switched (away )?from (.{3,40}) because",
    r"(.{3,40}) (doesn't support|has no support for|lacks|missing) (.{3,40})",
    r"abandoned (.{3,40}) (because|after|since)",
]

TOOL_NAMES = [
    "langchain", "llamaindex", "llama index", "openai", "anthropic",
    "hugging face", "huggingface", "chroma", "pinecone", "weaviate",
    "qdrant", "faiss", "pgvector", "ollama", "vllm", "tgi",
    "ragas", "deepeval", "promptfoo", "langsmith", "phoenix", "arize",
    "crew ai", "crewai", "autogen", "dspy", "haystack", "semantic kernel",
]

PERSONA_SIGNALS = {
    "indie builder": ["side project", "indie hacker", "solo founder", "building alone", "weekend project"],
    "ml engineer":   ["production ml", "ml pipeline", "model deployment", "inference", "serving"],
    "researcher":    ["paper", "reproduce", "benchmark", "dataset", "experiment", "arxiv"],
    "startup founder": ["startup", "early stage", "mvp", "launch", "raising", "seed"],
    "student":       ["learning", "course", "university", "assignment", "beginner", "tutorial"],
    "data scientist": ["jupyter", "notebook", "pandas", "sklearn", "analysis", "kaggle"],
}


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class ScoredQuote:
    text: str
    url: str
    score: float
    post_id: str = ""


@dataclass
class WorkaroundQuote:
    text: str
    url: str
    pattern_matched: str = ""


@dataclass
class ToolRejection:
    tool: str
    reason_snippet: str
    url: str


# ── Scoring functions ─────────────────────────────────────────────────────────

def intensity_score(post) -> float:
    """
    0.0–1.0 score based on engagement + frustration language density.
    """
    upvotes  = post.engagement or 0
    comments = post.comment_count or 0
    text     = ((post.title or "") + " " + (post.body or "")).lower()

    frustration_hits = sum(1 for w in FRUSTRATION_WORDS if w in text)
    kw_count         = post.keyword_count or 0

    # Normalise each component to 0–1 range
    upvote_norm   = min(upvotes  / 500, 1.0)
    comment_norm  = min(comments / 100, 1.0)
    frustration_n = min(frustration_hits / 5, 1.0)
    keyword_n     = min(kw_count / 6, 1.0)

    score = (0.35 * upvote_norm +
             0.25 * comment_norm +
             0.25 * frustration_n +
             0.15 * keyword_n)
    return round(score, 3)


def quote_quality_score(text: str, post) -> float:
    """
    0.0–1.0 score for a single quote/sentence.
    Rewards: specificity (length), tool mentions, frustration language.
    """
    text_lower = text.lower()

    length_score    = min(len(text.split()) / 30, 1.0)
    tool_hits       = sum(1 for t in TOOL_NAMES if t in text_lower)
    tool_score      = min(tool_hits / 2, 1.0)
    frustration_hits= sum(1 for w in FRUSTRATION_WORDS if w in text_lower)
    frustration_s   = min(frustration_hits / 3, 1.0)
    intensity       = intensity_score(post)

    score = (0.35 * length_score +
             0.25 * tool_score +
             0.25 * frustration_s +
             0.15 * intensity)
    return round(score, 3)


def rank_quotes(posts: list, top_n: int = 5) -> list[ScoredQuote]:
    """
    Extract and rank the best representative quotes from a cluster.
    Splits post bodies into sentences, scores each, returns top N.
    """
    candidates = []
    for post in posts:
        if not post.body:
            continue
        sentences = re.split(r'(?<=[.!?])\s+', post.body)
        for sent in sentences:
            sent = sent.strip()
            if len(sent.split()) < 6:
                continue
            score = quote_quality_score(sent, post)
            candidates.append(ScoredQuote(
                text=sent,
                url=post.url or "",
                score=score,
                post_id=post.id
            ))

    candidates.sort(key=lambda x: x.score, reverse=True)
    # Deduplicate: skip if first 60 chars overlap with an already-selected quote
    seen, selected = set(), []
    for q in candidates:
        key = q.text[:60].lower()
        if key not in seen:
            seen.add(key)
            selected.append(q)
        if len(selected) >= top_n:
            break
    return selected


def extract_workarounds(posts: list) -> list[WorkaroundQuote]:
    """
    Find sentences where people describe what they do instead of a proper solution.
    These are gold: they confirm pain is real and reveal the solution bar.
    """
    found = []
    for post in posts:
        text = (post.body or "") + " " + (post.title or "")
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sent in sentences:
            sent_lower = sent.lower()
            for pattern in WORKAROUND_PATTERNS:
                if re.search(pattern, sent_lower):
                    found.append(WorkaroundQuote(
                        text=sent.strip(),
                        url=post.url or "",
                        pattern_matched=pattern
                    ))
                    break
    return found[:6]


def extract_tool_rejections(posts: list) -> list[ToolRejection]:
    """
    Find mentions of tools people tried and abandoned.
    Reveals existing solutions and their specific failure modes.
    """
    found = []
    for post in posts:
        text = (post.body or "") + " " + (post.title or "")
        text_lower = text.lower()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sent in sentences:
            sent_lower = sent.lower()
            for pattern in TOOL_REJECTION_PATTERNS:
                match = re.search(pattern, sent_lower)
                if match:
                    # Try to identify which tool
                    tool = next((t for t in TOOL_NAMES if t in sent_lower), "unknown tool")
                    found.append(ToolRejection(
                        tool=tool,
                        reason_snippet=sent.strip()[:200],
                        url=post.url or ""
                    ))
                    break
    return found[:6]


def infer_persona(posts: list) -> str:
    """
    Rule-based persona inference from post text.
    Returns the most frequently matched persona label.
    """
    counts = {persona: 0 for persona in PERSONA_SIGNALS}
    for post in posts:
        text = ((post.title or "") + " " + (post.body or "")).lower()
        for persona, signals in PERSONA_SIGNALS.items():
            if any(s in text for s in signals):
                counts[persona] += 1

    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "builder"


def cluster_intensity(posts: list) -> float:
    """Average intensity score across all posts in a cluster."""
    if not posts:
        return 0.0
    scores = [intensity_score(p) for p in posts]
    return round(sum(scores) / len(scores), 3)


def evidence_quality(top_quotes: list[ScoredQuote]) -> float:
    """Average quote quality of the top quotes."""
    if not top_quotes:
        return 0.0
    return round(sum(q.score for q in top_quotes) / len(top_quotes), 3)
