"""Transcription via local Whisper; optional speaker labels from diarization."""
from pathlib import Path
from typing import Any

from app.config import WHISPER_MODEL
from app.services.diarization import assign_speaker_to_whisper_segment


def transcribe(
    audio_path: Path,
    diarization_segments: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Transcribe audio file with Whisper. Returns dict with:
    - full_text: str
    - segments: list of {start, end, text, speaker?}
    If diarization_segments is provided, each segment gets a "speaker" field.
    """
    import whisper

    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(str(audio_path), fp16=False)

    full_text = (result.get("text") or "").strip()
    segments = []
    for s in result.get("segments", []):
        start = s["start"]
        end = s["end"]
        text = (s.get("text") or "").strip()
        seg = {"start": start, "end": end, "text": text}
        if diarization_segments:
            speaker = assign_speaker_to_whisper_segment(
                start, end, diarization_segments
            )
            if speaker is not None:
                seg["speaker"] = speaker
        segments.append(seg)

    return {"full_text": full_text, "segments": segments}
