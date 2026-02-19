# Audio Sentiment Analysis Tool for Call Centers

Project path: `ai-projects/voice analyzer/`

An AI tool that analyzes call recordings from telecallers, performs **sentiment and tone analysis**, and delivers actionable feedback for companies to monitor agent performance and customer experience.

## Features

- **Audio ingestion**: Supports WAV, MP3, M4A, FLAC. Converts to 16 kHz mono for transcription.
- **Transcription**: Local Whisper (no API key required).
- **Sentiment & tone**: Positive/negative/neutral sentiment plus call-center tone labels (Professional, Frustrated, Apologetic, Neutral, Rushed).
- **Feedback report**: Per-call overall sentiment, tone summary, and 2–3 insight bullets.

## Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg (for audio conversion; install via `brew install ffmpeg` on macOS)

### Install

```bash
cd ai-projects/voice\ analyzer
# Or: cd "voice analyzer"  (if you are already in ai-projects)
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**FFmpeg** is required for audio conversion (WAV, MP3, M4A, FLAC). Install with:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

### Run the API

```bash
uvicorn app.main:app --reload
```

- **POST /analyze**: Upload an audio file (multipart), get analysis result.
- **GET /results**: List all results (optional query: `from_date`, `to_date` in ISO format).
- **GET /results/{result_id}**: Retrieve a stored result by ID.
- **GET /docs**: Swagger UI.

### Run the dashboard

With the API running, start the Streamlit dashboard (default: http://localhost:8501):

```bash
# From project root (voice analyzer), with .venv activated
streamlit run dashboard/streamlit_app.py
```

The dashboard shows a list of analyses (with date filters), per-call detail (transcript, sentiment, tone, insights), and an upload form in the sidebar. To point at another API, set `API_BASE_URL` in the environment (e.g. copy `dashboard/.env.example` to `dashboard/.env` and set `API_BASE_URL`).

### Example: Analyze an audio file

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@/path/to/call_recording.mp3"
```

## Project Structure

```
app/
├── main.py           # FastAPI app
├── config.py         # Settings, paths
├── services/
│   ├── audio.py      # Load, normalize, chunk audio
│   ├── transcription.py  # Whisper
│   ├── sentiment.py  # Sentiment + tone
│   └── feedback.py   # Per-call report + insights, list_results()
├── api/
│   └── routes.py     # POST /analyze, GET /results (list), GET /results/{id}
dashboard/
├── streamlit_app.py  # Streamlit UI: list, detail, upload
├── .env.example      # Optional: API_BASE_URL
storage/              # Audio + results storage
models/               # Optional model cache
```

## Environment

Copy `.env.example` to `.env` and adjust if needed. No API keys required for local Whisper.

If you see **SSL: CERTIFICATE_VERIFY_FAILED** (e.g. behind a corporate proxy with a self-signed certificate), set in `.env`:

```bash
DISABLE_SSL_VERIFY=1
```

Use only in trusted environments; this disables HTTPS verification for model downloads.

### Speaker diarization (who spoke when)

Optional **zero-cost** speaker diarization (e.g. Agent vs Customer) uses [pyannote-audio](https://github.com/pyannote/pyannote-audio) and runs locally after a one-time model download:

1. Create a Hugging Face token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Accept the model license: [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1).
3. Set in `.env`: `HF_TOKEN=your_token_here`.

If `HF_TOKEN` is not set, analysis runs without diarization (transcript and overall sentiment/tone only). Set `DIARIZATION_ENABLED=0` to disable even when a token is present.

## License

MIT
