"""Build per-call feedback report and insights from transcript + sentiment."""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import STORAGE_PATH
from app.services.sentiment import analyze_full_transcript

logger = logging.getLogger(__name__)


def build_feedback_report(
    transcript: dict[str, Any],
    sentiment_result: dict[str, Any],
    audio_filename: str = "",
    result_id: str | None = None,
) -> dict[str, Any]:
    """
    Build the per-call feedback object: overall sentiment, tone, segment breakdown, insights.
    Optionally persist to storage and return result_id.
    """
    result_id = result_id or str(uuid.uuid4())

    report = {
        "result_id": result_id,
        "audio_filename": audio_filename,
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
        "transcript": {
            "full_text": transcript.get("full_text", ""),
            "segment_count": len(transcript.get("segments", [])),
        },
        "overall_sentiment": sentiment_result.get("overall_sentiment", "neutral"),
        "overall_sentiment_score": sentiment_result.get("overall_sentiment_score", 0.0),
        "overall_sentiment_scores": sentiment_result.get("overall_sentiment_scores", {}),
        "overall_tone": sentiment_result.get("overall_tone", "Neutral"),
        "insights": sentiment_result.get("insights", []),
        "segment_breakdown": sentiment_result.get("segment_analyses", []),
    }
    if sentiment_result.get("by_speaker"):
        report["by_speaker"] = sentiment_result["by_speaker"]

    return report


def save_result(report: dict[str, Any]) -> Path:
    """Save report JSON to storage/results/{result_id}.json."""
    result_id = report["result_id"]
    path = STORAGE_PATH / "results" / f"{result_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


def load_result(result_id: str) -> dict[str, Any] | None:
    """Load a stored result by id."""
    path = STORAGE_PATH / "results" / f"{result_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def list_results(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[dict[str, Any]]:
    """
    List all results as summaries. Optional from_date/to_date filter by analyzed_at (inclusive).
    Sorted by analyzed_at descending. Skips corrupt files.
    """
    results_dir = STORAGE_PATH / "results"
    if not results_dir.exists():
        return []

    summaries: list[dict[str, Any]] = []
    for path in results_dir.glob("*.json"):
        try:
            with open(path) as f:
                report = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Skip corrupt or unreadable result %s: %s", path.name, e)
            continue

        analyzed_at_str = report.get("analyzed_at") or ""
        try:
            analyzed_at = datetime.fromisoformat(
                analyzed_at_str.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            analyzed_at = None

        if from_date and analyzed_at is not None and analyzed_at < from_date:
            continue
        if to_date and analyzed_at is not None and analyzed_at > to_date:
            continue

        summaries.append({
            "result_id": report.get("result_id", ""),
            "audio_filename": report.get("audio_filename", ""),
            "analyzed_at": analyzed_at_str,
            "overall_sentiment": report.get("overall_sentiment", "neutral"),
            "overall_sentiment_score": report.get("overall_sentiment_score", 0.0),
            "overall_tone": report.get("overall_tone", "Neutral"),
            "insights": report.get("insights", []),
        })

    summaries.sort(
        key=lambda s: s["analyzed_at"] or "",
        reverse=True,
    )
    return summaries
