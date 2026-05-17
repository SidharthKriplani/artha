"""
artha-ai.sig — Database connection and helpers
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from storage.models import Base

DB_PATH = Path(__file__).parent.parent / "data" / "artha.db"
DB_URL  = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()


def load_posts_for_scan(session: Session, communities: list[str] = None,
                        min_signal_score: int = 1, limit: int = 2000):
    """
    Load posts from DB for intelligence pipeline.
    Optionally filter by community and minimum signal score.
    """
    from storage.models import Post
    q = session.query(Post)
    if communities:
        q = q.filter(Post.community.in_(communities))
    q = q.filter(Post.signal_score >= min_signal_score)
    q = q.order_by(Post.fetched_at.desc()).limit(limit)
    return q.all()
