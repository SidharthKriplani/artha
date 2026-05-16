"""
ARTHA — Streamlit UI
Evidence pack viewer for AI/ML builder pain signals.
Run: streamlit run ui/app.py
"""

import sys
import os
import json
import uuid
import time
import requests
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

API_BASE = "http://localhost:8000"
REPORT_DIR = Path(__file__).parent.parent / "data" / "reports"
CSV_PATH   = Path(__file__).parent.parent / "data" / "pain_signals.csv"

st.set_page_config(
    page_title="ARTHA — Pain Signal Intelligence",
    page_icon="🔍",
    layout="wide"
)

# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.signal-card { padding: 1rem; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 1rem; }
.score-high   { color: #d32f2f; font-weight: bold; }
.score-med    { color: #f57c00; font-weight: bold; }
.score-low    { color: #388e3c; }
.quote-box    { background: #f5f5f5; padding: 0.75rem; border-left: 3px solid #1565c0;
                margin: 0.5rem 0; border-radius: 0 4px 4px 0; font-style: italic; }
.workaround   { background: #fff8e1; padding: 0.75rem; border-left: 3px solid #f9a825;
                margin: 0.5rem 0; border-radius: 0 4px 4px 0; }
.rejection    { background: #fce4ec; padding: 0.75rem; border-left: 3px solid #c62828;
                margin: 0.5rem 0; border-radius: 0 4px 4px 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🔍 ARTHA")
st.caption("AI/ML Builder Pain Signal Intelligence · Evidence-based, not inspiration-based")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Controls")

    mode = st.radio("Mode", ["Run New Scan", "Load Existing Report", "Browse Raw Signals"])

    if mode == "Run New Scan":
        try:
            resp = requests.get(f"{API_BASE}/communities", timeout=3)
            all_communities = resp.json()["communities"]
        except Exception:
            all_communities = [
                "LocalLLaMA", "MachineLearning", "LanguageModelHacking",
                "SideProject", "devtools", "developersIndia", "indianstartups"
            ]

        selected = st.multiselect(
            "Communities", all_communities, default=all_communities[:4]
        )
        min_score = st.slider("Min signal score", 1, 3, 2)
        run_btn = st.button("Run Scan", type="primary", use_container_width=True)

    elif mode == "Load Existing Report":
        report_files = sorted(REPORT_DIR.glob("*.json"), reverse=True) if REPORT_DIR.exists() else []
        if report_files:
            selected_report = st.selectbox(
                "Select report",
                [f.stem for f in report_files],
                format_func=lambda x: x[:16] + "..."
            )
        else:
            st.info("No reports yet. Run a scan first.")
            selected_report = None

    st.divider()
    st.caption("Built by @SidharthKriplani")
    st.caption("Signals sourced from real developer communities")


# ── Main content ──────────────────────────────────────────────────────────────

def render_evidence_pack(pack: dict, idx: int):
    intensity  = pack.get("intensity_score", 0)
    freq       = pack.get("frequency", 0)
    eq         = pack.get("evidence_quality", 0)
    label      = pack.get("label", "Unknown")
    persona    = pack.get("detected_persona", "builder")
    communities= pack.get("communities", [])
    anchor     = pack.get("anchor", {})

    # Score colour
    score_class = "score-high" if intensity > 0.6 else "score-med" if intensity > 0.3 else "score-low"

    with st.expander(f"**{idx}. {label.upper()}**  ·  {freq} posts  ·  intensity {intensity:.2f}", expanded=idx == 1):

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Pain Frequency", freq)
        col2.metric("Signal Intensity", f"{intensity:.2f}")
        col3.metric("Evidence Quality", f"{eq:.2f}")
        col4.metric("Persona", persona.title())

        if communities:
            st.caption(f"Communities: {' · '.join(['r/'+c for c in communities])}")

        if anchor.get("title"):
            st.markdown(f"**Top signal:** [{anchor['title'][:90]}...]({anchor['url']})  "
                        f"↑{anchor.get('upvotes',0)}  💬{anchor.get('comments',0)}")

        st.divider()

        # Top quotes
        quotes = pack.get("top_quotes", [])
        if quotes:
            st.markdown("**Representative Quotes**")
            for q in quotes[:3]:
                st.markdown(
                    f'<div class="quote-box">"{q["text"]}" '
                    f'<a href="{q["url"]}" target="_blank">[source]</a></div>',
                    unsafe_allow_html=True
                )

        # Workarounds
        workarounds = pack.get("workaround_patterns", [])
        if workarounds:
            st.markdown("**What People Do Instead** *(workaround signals)*")
            for w in workarounds[:3]:
                st.markdown(
                    f'<div class="workaround">{w["text"]} '
                    f'<a href="{w["url"]}" target="_blank">[source]</a></div>',
                    unsafe_allow_html=True
                )

        # Tool rejections
        rejections = pack.get("tool_rejections", [])
        if rejections:
            st.markdown("**Tools Tried & Rejected**")
            for r in rejections[:3]:
                st.markdown(
                    f'<div class="rejection"><strong>{r["tool"].title()}</strong>: {r["reason"][:150]} '
                    f'<a href="{r["url"]}" target="_blank">[source]</a></div>',
                    unsafe_allow_html=True
                )

        # Where to find these people
        reachable = pack.get("reachable_communities", [])
        if reachable:
            st.markdown(f"**Where to find them:** {' · '.join(reachable)}")

        st.divider()
        col_a, col_b = st.columns(2)
        col_a.download_button(
            "Export this pack (JSON)",
            data=json.dumps(pack, indent=2),
            file_name=f"evidence_pack_{pack.get('cluster_id','x')}.json",
            mime="application/json",
            key=f"dl_{idx}"
        )


def render_report(report: dict):
    packs = report.get("evidence_packs", [])
    total_posts    = report.get("total_posts", 0)
    total_clusters = report.get("total_clusters", 0)

    st.subheader(f"Scan Report · {total_posts} posts · {total_clusters} pain clusters")
    st.caption(f"Generated: {report.get('generated_at','')[:19]}")

    if not packs:
        st.warning("No clusters found. Try lowering the min signal score or running the scraper first.")
        return

    for idx, pack in enumerate(packs, 1):
        render_evidence_pack(pack, idx)

    # Full export
    st.download_button(
        "Export full report (JSON)",
        data=json.dumps(report, indent=2),
        file_name=f"artha_report_{report.get('scan_id','')[:8]}.json",
        mime="application/json"
    )


# ── Mode routing ──────────────────────────────────────────────────────────────

if mode == "Run New Scan":
    if run_btn:
        if not selected:
            st.warning("Select at least one community.")
        else:
            with st.spinner("Running intelligence pipeline..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/scan",
                        json={"communities": selected, "min_signal_score": min_score},
                        timeout=5
                    )
                    scan_id = resp.json()["scan_id"]
                    st.info(f"Scan started: `{scan_id}`")

                    # Poll for completion
                    progress = st.progress(0, text="Embedding posts...")
                    for i in range(60):
                        time.sleep(3)
                        check = requests.get(f"{API_BASE}/report/{scan_id}", timeout=5).json()
                        progress.progress(min((i + 1) * 5, 95), text="Processing clusters...")
                        if check.get("status") in (None, "complete"):
                            progress.progress(100, text="Done.")
                            break

                    report_path = REPORT_DIR / f"{scan_id}.json"
                    if report_path.exists():
                        with open(report_path) as f:
                            report = json.load(f)
                        render_report(report)
                    else:
                        st.error("Pipeline did not complete. Check that the API is running.")

                except requests.exceptions.ConnectionError:
                    st.error("API not running. Start it with: `uvicorn api.main:app --reload`")
    else:
        st.info("Select communities and click **Run Scan** to start.")

elif mode == "Load Existing Report":
    if selected_report:
        report_path = REPORT_DIR / f"{selected_report}.json"
        with open(report_path) as f:
            report = json.load(f)
        render_report(report)

elif mode == "Browse Raw Signals":
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        st.subheader(f"Raw Pain Signals · {len(df)} total")

        col1, col2 = st.columns(2)
        score_filter = col1.multiselect("Signal Score", [1, 2, 3], default=[2, 3])
        sub_filter   = col2.multiselect("Subreddit", sorted(df["subreddit"].unique()))

        filtered = df[df["score"].isin(score_filter)]
        if sub_filter:
            filtered = filtered[filtered["subreddit"].isin(sub_filter)]

        filtered = filtered.sort_values("score", ascending=False)
        st.dataframe(
            filtered[["date", "subreddit", "title", "upvotes", "comments",
                       "score", "matched_keywords", "url"]],
            use_container_width=True,
            hide_index=True,
            column_config={"url": st.column_config.LinkColumn("url")}
        )

        st.download_button(
            "Download filtered CSV",
            data=filtered.to_csv(index=False),
            file_name="artha_signals_filtered.csv",
            mime="text/csv"
        )
    else:
        st.info("No signals yet. Run the digest scraper first: `python3 digest/scraper.py`")
