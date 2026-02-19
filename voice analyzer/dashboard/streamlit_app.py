"""Streamlit dashboard for Audio Sentiment Analysis: list results, detail view, upload."""
import os
from datetime import datetime

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def fetch_results(from_date: str | None = None, to_date: str | None = None) -> list[dict]:
    """GET /results with optional date filters."""
    params = {}
    if from_date:
        params["from_date"] = from_date
    if to_date:
        params["to_date"] = to_date
    r = requests.get(f"{API_BASE_URL}/results", params=params or None, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_result(result_id: str) -> dict:
    """GET /results/{result_id}."""
    r = requests.get(f"{API_BASE_URL}/results/{result_id}", timeout=30)
    r.raise_for_status()
    return r.json()


def upload_audio(file) -> dict:
    """POST /analyze with file."""
    files = {"file": (file.name, file.getvalue(), file.type or "audio/mpeg")}
    r = requests.post(f"{API_BASE_URL}/analyze", files=files, timeout=300)
    r.raise_for_status()
    return r.json()


def format_analyzed_at(iso_str: str) -> str:
    """Format analyzed_at for display."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_str


def sentiment_badge(sentiment: str) -> str:
    """Return a short label for sentiment."""
    s = (sentiment or "neutral").lower()
    if s == "positive":
        return "Positive"
    if s == "negative":
        return "Negative"
    return "Neutral"


def render_list_view():
    st.title("Call sentiment analysis")
    st.caption("View and filter analysis results. Use the sidebar to upload new audio.")

    if "filter_from" not in st.session_state:
        st.session_state.filter_from = None
    if "filter_to" not in st.session_state:
        st.session_state.filter_to = None

    col_from, col_to, col_btn = st.columns([1, 1, 1])
    with col_from:
        from_date = st.date_input("From date", value=None, key="from_date")
    with col_to:
        to_date = st.date_input("To date", value=None, key="to_date")
    with col_btn:
        apply = st.button("Apply filters")
    if apply:
        st.session_state.filter_from = from_date
        st.session_state.filter_to = to_date

    from_iso = None
    to_iso = None
    if st.session_state.filter_from is not None:
        from_iso = st.session_state.filter_from.isoformat()
    if st.session_state.filter_to is not None:
        to_iso = f"{st.session_state.filter_to.isoformat()}T23:59:59"

    try:
        results = fetch_results(from_date=from_iso, to_date=to_iso)
    except requests.RequestException as e:
        st.error(f"Could not load results. Is the API running at {API_BASE_URL}? Error: {e}")
        return

    if not results:
        st.info("No results found. Upload an audio file from the sidebar to get started.")
        return

    st.subheader(f"Results ({len(results)})")
    for row in results:
        with st.container():
            rid = row.get("result_id", "")
            filename = row.get("audio_filename", "—")
            analyzed = format_analyzed_at(row.get("analyzed_at", ""))
            sentiment = sentiment_badge(row.get("overall_sentiment", ""))
            tone = row.get("overall_tone", "—")
            insights = row.get("insights", [])[:2]
            insight_text = " | ".join(insights) if insights else "—"

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{filename}**")
                st.caption(f"{analyzed} · {sentiment} · {tone}")
                if insight_text != "—":
                    st.caption(insight_text)
            with col3:
                if st.button("View", key=f"view_{rid}", type="primary"):
                    st.query_params["result_id"] = rid
                    st.rerun()
            st.divider()


def render_detail_view(result_id: str):
    try:
        report = fetch_result(result_id)
    except requests.RequestException as e:
        st.error(f"Could not load result. Error: {e}")
        if st.button("Back to list"):
            st.query_params.clear()
            st.rerun()
        return

    st.title("Analysis detail")
    if st.button("← Back to list"):
        st.query_params.clear()
        st.rerun()

    st.write(f"**File:** {report.get('audio_filename', '—')}")
    st.write(f"**Analyzed:** {format_analyzed_at(report.get('analyzed_at', ''))}")
    st.write(f"**Sentiment:** {sentiment_badge(report.get('overall_sentiment', ''))} "
             f"(score: {report.get('overall_sentiment_score', 0):.2f})")
    st.write(f"**Tone:** {report.get('overall_tone', '—')}")

    by_speaker = report.get("by_speaker") or {}
    if by_speaker:
        st.subheader("By speaker")
        for speaker, data in by_speaker.items():
            st.write(f"**{speaker}:** sentiment {data.get('sentiment', '—')} "
                     f"(score: {data.get('sentiment_score', 0):.2f}), tone: {data.get('tone', '—')}")

    st.subheader("Insights")
    for insight in report.get("insights", []):
        st.markdown(f"- {insight}")

    st.subheader("Transcript")
    full_text = (report.get("transcript") or {}).get("full_text", "")
    if full_text:
        st.text_area("Full text", value=full_text, height=200, disabled=True, label_visibility="collapsed")
    else:
        st.caption("No transcript.")

    segment_breakdown = report.get("segment_breakdown", [])
    if segment_breakdown:
        with st.expander("Segment breakdown"):
            for seg in segment_breakdown[:20]:
                start = seg.get("start", 0)
                end = seg.get("end", 0)
                text = (seg.get("text") or "")[:150]
                sent = seg.get("sentiment", "—")
                tone_seg = seg.get("tone", "—")
                sp = seg.get("speaker", "")
                prefix = f"[{start:.1f}s–{end:.1f}s]"
                if sp:
                    prefix += f" {sp}"
                st.caption(f"{prefix} {sent} · {tone_seg}: {text}...")
            if len(segment_breakdown) > 20:
                st.caption(f"... and {len(segment_breakdown) - 20} more segments.")


def main():
    st.set_page_config(page_title="Call sentiment analysis", page_icon="📞", layout="wide")

    result_id = st.query_params.get("result_id")
    if result_id:
        render_detail_view(result_id)
        return

    with st.sidebar:
        st.subheader("Upload audio")
        uploaded = st.file_uploader(
            "Choose an audio file (WAV, MP3, M4A, FLAC)",
            type=["wav", "mp3", "m4a", "flac"],
            key="upload",
        )
        if uploaded and st.button("Analyze"):
            with st.spinner("Transcribing and analyzing…"):
                try:
                    report = upload_audio(uploaded)
                    rid = report.get("result_id", "")
                    st.success(f"Done. Result ID: {rid[:8]}…")
                    if st.button("View this result"):
                        st.query_params["result_id"] = rid
                        st.rerun()
                except requests.RequestException as e:
                    detail = str(e)
                    if getattr(e, "response", None) is not None:
                        try:
                            detail = e.response.json().get("detail", detail)
                        except Exception:
                            pass
                    st.error(f"Upload failed: {detail}")

    render_list_view()


if __name__ == "__main__":
    main()
