"""Application settings, paths, and model names."""
import os
import ssl
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Optional: disable SSL verification (e.g. behind corporate proxy with self-signed cert)
if os.getenv("DISABLE_SSL_VERIFY", "").lower() in ("1", "true", "yes"):
    ssl._create_default_https_context = ssl._create_unverified_context

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", str(BASE_DIR / "storage")))
MODELS_PATH = BASE_DIR / "models"

# Ensure dirs exist
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
(STORAGE_PATH / "audio").mkdir(exist_ok=True)
(STORAGE_PATH / "results").mkdir(exist_ok=True)

# Whisper
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Audio pipeline
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION_SEC = 30 * 60  # 30 min chunks for long calls
MAX_FILE_SIZE_MB = 100

# Sentiment model (Hugging Face)
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Speaker diarization (pyannote) - requires HF token to download model once; then runs locally
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
DIARIZATION_ENABLED = os.getenv("DIARIZATION_ENABLED", "1").lower() in ("1", "true", "yes")
PYANNOTE_DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
