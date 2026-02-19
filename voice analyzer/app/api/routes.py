"""API routes: POST /analyze, GET /results (list), GET /results/{result_id}."""
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import STORAGE_PATH
from app.services.audio import load_and_normalize
from app.services.diarization import diarize
from app.services.feedback import (
    build_feedback_report,
    list_results,
    load_result,
    save_result,
)
from app.services.sentiment import analyze_full_transcript
from app.services.transcription import transcribe

router = APIRouter()


@router.get("/")
async def root():
    """Health check and API info."""
    return {"service": "Audio Sentiment Analysis Tool", "docs": "/docs"}


@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Upload an audio file (WAV, MP3, M4A, FLAC). Runs transcription and
    sentiment/tone analysis; returns feedback report and stores result.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    suffix = Path(file.filename).suffix or ".bin"
    upload_path = STORAGE_PATH / "audio" / f"{uuid.uuid4()}{suffix}"
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    try:
        normalized_path = load_and_normalize(upload_path)
    except Exception as e:
        err_msg = str(e).lower()
        if (
            "ffmpeg" in err_msg
            or "avconv" in err_msg
            or "ffprobe" in err_msg
            or "could not find" in err_msg
            or "decoder" in err_msg
            or "no such file" in err_msg
            or isinstance(e, (FileNotFoundError, OSError))
        ):
            detail = (
                "Audio conversion failed. FFmpeg is required for MP3, M4A, FLAC, etc. "
                "Install it (e.g. macOS: brew install ffmpeg, Ubuntu: sudo apt install ffmpeg) and try again."
            )
        else:
            detail = f"Invalid or unsupported audio: {e}"
        raise HTTPException(status_code=400, detail=detail)

    diarization_segments = diarize(normalized_path, num_speakers=2)
    try:
        transcript = transcribe(normalized_path, diarization_segments=diarization_segments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    full_text = transcript.get("full_text", "")
    segments = transcript.get("segments", [])

    sentiment_result = analyze_full_transcript(full_text, segments)

    report = build_feedback_report(
        transcript=transcript,
        sentiment_result=sentiment_result,
        audio_filename=file.filename,
    )
    save_result(report)

    return report


@router.get("/results")
async def list_results_endpoint(
    from_date: str | None = None,
    to_date: str | None = None,
):
    """
    List all analysis results (summaries). Optional from_date, to_date in ISO format
    to filter by analyzed_at (inclusive). Sorted newest first.
    """
    from_dt = None
    to_dt = None
    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="from_date must be ISO format (e.g. 2025-01-01 or 2025-01-01T00:00:00Z)",
            )
    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="to_date must be ISO format (e.g. 2025-01-01 or 2025-01-01T23:59:59Z)",
            )
    summaries = list_results(from_date=from_dt, to_date=to_dt)
    return summaries


@router.get("/results/{result_id}")
async def get_result(result_id: str):
    """Retrieve a stored analysis result by id."""
    report = load_result(result_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return report
