"""
ARTHA — Storage Models
Source-aware schema. Designed to accept Reddit, HN, GitHub, and other sources
without schema changes.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, JSON, create_engine
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Post(Base):
    """
    Normalised representation of a post/thread from any source.
    Currently populated from Reddit. HN and GitHub adapters plug in later
    without changing this schema.
    """
    __tablename__ = "posts"

    id               = Column(String, primary_key=True)   # "{source}:{post_id}"
    source           = Column(String, nullable=False)      # "reddit" | "hn" | "github"
    community        = Column(String, nullable=False)      # subreddit / repo / tag
    thread_id        = Column(String, nullable=False)
    parent_id        = Column(String, nullable=True)
    timestamp        = Column(DateTime, nullable=True)
    title            = Column(Text, nullable=True)
    body             = Column(Text, nullable=True)
    url              = Column(String, nullable=True)
    engagement       = Column(Integer, default=0)          # upvotes / score
    comment_count    = Column(Integer, default=0)
    author_context   = Column(String, nullable=True)
    tags_flair       = Column(String, nullable=True)
    fetched_at       = Column(DateTime, default=datetime.utcnow)

    # Signal fields (populated by intelligence layer)
    matched_keywords = Column(Text, nullable=True)
    keyword_count    = Column(Integer, default=0)
    signal_score     = Column(Integer, default=1)          # 1–3
    embedding_id     = Column(String, nullable=True)       # FK to embeddings store


class ClusterResult(Base):
    """
    Output of one clustering run across a set of posts.
    Each row = one pain cluster.
    """
    __tablename__ = "cluster_results"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    scan_id          = Column(String, nullable=False)      # UUID per run
    cluster_label    = Column(String, nullable=True)       # TF-IDF derived
    frequency        = Column(Integer, default=0)          # posts in cluster
    intensity_score  = Column(Float, default=0.0)          # avg signal strength
    evidence_quality = Column(Float, default=0.0)          # quote quality score
    top_quotes       = Column(JSON, nullable=True)         # [{text, url, score}]
    workaround_quotes= Column(JSON, nullable=True)         # [{text, url}]
    tool_rejections  = Column(JSON, nullable=True)         # [{tool, reason, url}]
    detected_persona = Column(String, nullable=True)
    communities      = Column(JSON, nullable=True)         # which subreddits contributed
    created_at       = Column(DateTime, default=datetime.utcnow)


class ScanRun(Base):
    """
    Metadata for each intelligence pipeline run.
    """
    __tablename__ = "scan_runs"

    id               = Column(String, primary_key=True)    # UUID
    communities      = Column(JSON, nullable=True)
    keyword_filter   = Column(String, nullable=True)
    post_count       = Column(Integer, default=0)
    cluster_count    = Column(Integer, default=0)
    status           = Column(String, default="pending")   # pending|running|complete|failed
    started_at       = Column(DateTime, default=datetime.utcnow)
    completed_at     = Column(DateTime, nullable=True)
