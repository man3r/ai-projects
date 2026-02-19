"""Speaker diarization via pyannote-audio (local, zero recurring cost)."""
import logging
from pathlib import Path
from typing import Any

from app.config import (
    DIARIZATION_ENABLED,
    HF_TOKEN,
    PYANNOTE_DIARIZATION_MODEL,
)

logger = logging.getLogger(__name__)

_diarization_pipeline = None


def _load_pipeline():
    global _diarization_pipeline
    if _diarization_pipeline is not None:
        return _diarization_pipeline
    if not HF_TOKEN or not DIARIZATION_ENABLED:
        return None
    try:
        from pyannote.audio import Pipeline
        _diarization_pipeline = Pipeline.from_pretrained(
            PYANNOTE_DIARIZATION_MODEL,
            use_auth_token=HF_TOKEN,
        )
        return _diarization_pipeline
    except Exception as e:
        logger.warning("Could not load pyannote diarization pipeline: %s", e)
        return None


def diarize(audio_path: Path, num_speakers: int | None = 2) -> list[dict[str, Any]] | None:
    """
    Run speaker diarization on audio. Returns list of {"start", "end", "speaker"}
    or None if diarization is disabled or fails (caller can proceed without speakers).
    """
    pipeline = _load_pipeline()
    if pipeline is None:
        return None
    try:
        kwargs = {"num_speakers": num_speakers} if num_speakers else {}
        diarization = pipeline(str(audio_path), **kwargs)
    except Exception as e:
        logger.warning("Diarization failed for %s: %s", audio_path.name, e)
        return None

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": float(turn.start),
            "end": float(turn.end),
            "speaker": str(speaker),
        })
    return segments


def assign_speaker_to_whisper_segment(
    seg_start: float,
    seg_end: float,
    diar_segments: list[dict[str, Any]],
) -> str | None:
    """
    Assign a speaker to a Whisper segment by maximum overlap with diarization segments.
    Returns speaker label or None if no overlap.
    """
    if not diar_segments:
        return None
    seg_mid = (seg_start + seg_end) / 2
    best_speaker = None
    best_overlap = 0.0
    for d in diar_segments:
        d_start = d["start"]
        d_end = d["end"]
        overlap_start = max(seg_start, d_start)
        overlap_end = min(seg_end, d_end)
        if overlap_end > overlap_start:
            overlap = overlap_end - overlap_start
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = d["speaker"]
    if best_speaker is not None:
        return best_speaker
    # Fallback: speaker at segment midpoint
    for d in diar_segments:
        if d["start"] <= seg_mid <= d["end"]:
            return d["speaker"]
    return None
