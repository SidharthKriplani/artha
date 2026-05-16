"""
ARTHA — FastAPI Backend
Endpoints for running scans, retrieving reports, listing communities.
"""

import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from storage.database import init_db, get_session, load_posts_for_scan
from storage.models import ScanRun
from intelligence.embeddings import generate_embeddings
from intelligence.clustering import cluster_posts
from intelligence.report import build_scan_report

app = FastAPI(
    title="ARTHA",
    description="AI/ML Builder Pain Signal Intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COMMUNITIES = [
    "LocalLLaMA",
    "MachineLearning",
    "LanguageModelHacking",
    "SideProject",
    "devtools",
    "developersIndia",
    "indianstartups",
]


@app.on_event("startup")
def startup():
    init_db()


# ── Request/Response models ───────────────────────────────────────────────────

class ScanRequest(BaseModel):
    communities: list[str] = COMMUNITIES
    keyword_filter: Optional[str] = None
    min_signal_score: int = 1


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/communities")
def list_communities():
    return {"communities": COMMUNITIES}


@app.post("/scan", response_model=ScanResponse)
def trigger_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    session = get_session()

    run = ScanRun(
        id=scan_id,
        communities=req.communities,
        keyword_filter=req.keyword_filter,
        status="pending",
        started_at=datetime.utcnow()
    )
    session.add(run)
    session.commit()

    background_tasks.add_task(
        run_pipeline, scan_id, req.communities,
        req.min_signal_score
    )

    return ScanResponse(
        scan_id=scan_id,
        status="started",
        message=f"Scan {scan_id} started. Poll /report/{scan_id} for results."
    )


def run_pipeline(scan_id: str, communities: list[str], min_score: int):
    session = get_session()
    try:
        run = session.query(ScanRun).filter_by(id=scan_id).first()
        run.status = "running"
        session.commit()

        posts = load_posts_for_scan(session, communities, min_score)
        if not posts:
            run.status = "failed"
            run.completed_at = datetime.utcnow()
            session.commit()
            return

        embeddings = generate_embeddings(posts)
        clusters   = cluster_posts(embeddings, posts)
        report     = build_scan_report(clusters, scan_id)

        run.status        = "complete"
        run.post_count    = report["total_posts"]
        run.cluster_count = report["total_clusters"]
        run.completed_at  = datetime.utcnow()

        # Store report as JSON in metadata field
        import json
        from pathlib import Path
        report_dir = Path(__file__).parent.parent / "data" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        with open(report_dir / f"{scan_id}.json", "w") as f:
            json.dump(report, f, indent=2)

        session.commit()

    except Exception as e:
        run = session.query(ScanRun).filter_by(id=scan_id).first()
        if run:
            run.status = "failed"
            session.commit()
        raise e
    finally:
        session.close()


@app.get("/report/{scan_id}")
def get_report(scan_id: str):
    import json
    from pathlib import Path

    report_path = Path(__file__).parent.parent / "data" / "reports" / f"{scan_id}.json"
    if not report_path.exists():
        # Check if scan is still running
        session = get_session()
        run = session.query(ScanRun).filter_by(id=scan_id).first()
        session.close()
        if run:
            return {"scan_id": scan_id, "status": run.status}
        raise HTTPException(status_code=404, detail="Scan not found")

    with open(report_path) as f:
        return json.load(f)


@app.get("/scans")
def list_scans(limit: int = 10):
    session = get_session()
    runs = session.query(ScanRun).order_by(
        ScanRun.started_at.desc()
    ).limit(limit).all()
    session.close()
    return {
        "scans": [
            {
                "id": r.id,
                "status": r.status,
                "communities": r.communities,
                "post_count": r.post_count,
                "cluster_count": r.cluster_count,
                "started_at": str(r.started_at),
                "completed_at": str(r.completed_at),
            }
            for r in runs
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
