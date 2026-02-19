"""Load, normalize, and optionally chunk audio for transcription."""
from pathlib import Path
from typing import Optional

from pydub import AudioSegment

from app.config import CHANNELS, SAMPLE_RATE, STORAGE_PATH


def load_and_normalize(
    input_path: Path,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Load audio from path (WAV, MP3, M4A, FLAC), convert to 16 kHz mono,
    and save as WAV. Returns path to the normalized file.
    """
    segment = AudioSegment.from_file(str(input_path))
    segment = segment.set_channels(CHANNELS)
    segment = segment.set_frame_rate(SAMPLE_RATE)
    # Whisper expects 16-bit PCM
    segment = segment.set_sample_width(2)

    if output_path is None:
        output_path = STORAGE_PATH / "audio" / (input_path.stem + "_normalized.wav")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    segment.export(str(output_path), format="wav", parameters=["-ar", str(SAMPLE_RATE)])
    return output_path


def get_duration_seconds(path: Path) -> float:
    """Return duration of audio file in seconds."""
    segment = AudioSegment.from_file(str(path))
    return len(segment) / 1000.0
