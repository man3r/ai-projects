# Building an AI-Powered Voice Analyzer for Call Centers -- A Technical Deep Dive

**TL;DR:** I built a tool that takes call center recordings and automatically extracts transcripts, sentiment, tone, speaker identification, and actionable insights -- all running locally with zero API costs. Here's how I designed and built it.

---

## The Problem

Call centers generate thousands of hours of recordings daily. Manually reviewing them for quality assurance is slow, expensive, and inconsistent. I wanted to build a tool that could:

- Transcribe call recordings automatically
- Identify who said what (agent vs. customer)
- Analyze sentiment and tone per speaker
- Generate actionable insights for managers

The constraint: everything had to run **locally** -- no per-call API fees, no data leaving the machine.

---

## Architecture Overview

The system is split into two components: a **FastAPI backend** that handles the heavy AI processing, and a **Streamlit dashboard** for visualization and interaction.

```
                    +---------------------+
                    |  Streamlit Dashboard |
                    |    (localhost:8501)  |
                    +----------+----------+
                               |
                          HTTP/REST
                               |
                    +----------v----------+
                    |   FastAPI Backend    |
                    |    (localhost:8000)  |
                    +----------+----------+
                               |
              +----------------+----------------+
              |                |                |
        +-----v-----+   +-----v-----+   +-----v-----+
        |   Whisper  |   |  Pyannote |   |  RoBERTa  |
        |   (STT)    |   | (Diarize) |   | (Sentiment)|
        +-----+------+   +-----+-----+   +-----+-----+
              |                |                |
              +----------------+----------------+
                               |
                    +----------v----------+
                    |   JSON File Storage  |
                    |    storage/results/  |
                    +---------------------+
```

I deliberately avoided a database. Each analysis result is a self-contained JSON file identified by UUID. This makes the system portable -- you can copy the `storage/` folder to another machine and everything works.

---

## The Processing Pipeline

When an audio file is uploaded, it passes through five stages:

### 1. Audio Normalization

Call recordings come in all shapes: MP3, M4A, FLAC, varying sample rates. The first step standardizes everything to 16kHz mono WAV -- the format Whisper expects.

```python
def load_and_normalize(input_path: Path, output_path: Optional[Path] = None) -> Path:
    segment = AudioSegment.from_file(str(input_path))
    segment = segment.set_channels(1)          # mono
    segment = segment.set_frame_rate(16000)     # 16kHz
    segment = segment.set_sample_width(2)       # 16-bit PCM
    segment.export(str(output_path), format="wav")
    return output_path
```

I chose `pydub` over `librosa` for the conversion step because it handles format detection and FFmpeg integration cleanly. The tradeoff is an external FFmpeg dependency, but it's a one-line install on any platform.

### 2. Speaker Diarization (Optional)

Before transcription, I optionally run pyannote's speaker diarization model to identify _who_ spoke _when_. This is the most computationally expensive step, but it's what turns a flat transcript into a conversation.

```python
def diarize(audio_path: Path, num_speakers: int | None = 2) -> list[dict] | None:
    pipeline = _load_pipeline()   # pyannote/speaker-diarization-3.1
    if pipeline is None:
        return None
    diarization = pipeline(str(audio_path), num_speakers=num_speakers)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": float(turn.start),
            "end": float(turn.end),
            "speaker": str(speaker),
        })
    return segments
```

A key design decision: diarization is **optional and gracefully degraded**. If the user doesn't have a Hugging Face token, or if the model fails, the pipeline continues without speaker labels. No crash, no error -- just less information in the output.

### 3. Transcription

OpenAI's Whisper runs locally. No API key, no per-minute charges. The `base` model strikes a good balance between accuracy and speed for call center audio (which is typically clear speech, not noisy environments).

The interesting part is merging Whisper's output with diarization. Whisper produces timestamped segments; I assign speakers by finding the diarization segment with maximum overlap:

```python
def assign_speaker_to_whisper_segment(seg_start, seg_end, diar_segments):
    best_speaker = None
    best_overlap = 0.0
    for d in diar_segments:
        overlap_start = max(seg_start, d["start"])
        overlap_end = min(seg_end, d["end"])
        if overlap_end > overlap_start:
            overlap = overlap_end - overlap_start
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = d["speaker"]
    if best_speaker is not None:
        return best_speaker
    # Fallback: speaker at segment midpoint
    seg_mid = (seg_start + seg_end) / 2
    for d in diar_segments:
        if d["start"] <= seg_mid <= d["end"]:
            return d["speaker"]
    return None
```

The midpoint fallback handles edge cases where Whisper and pyannote disagree on segment boundaries.

### 4. Sentiment Analysis

For sentiment, I use the `cardiffnlp/twitter-roberta-base-sentiment-latest` model from Hugging Face. It classifies text as positive, negative, or neutral with confidence scores. The model is loaded lazily as a singleton -- no repeated initialization across segments:

```python
_sentiment_pipeline = None

def _get_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline("sentiment-analysis", model=SENTIMENT_MODEL, top_k=None)
    return _sentiment_pipeline
```

Sentiment runs at three levels: overall transcript, per-segment, and per-speaker (when diarization is available). Per-speaker sentiment is particularly useful -- it lets managers see if the customer was frustrated while the agent remained professional.

### 5. Tone Detection

On top of ML-based sentiment, I added a keyword-driven tone classifier. This is deliberately simple -- a lookup against curated keyword lists for five call-center-relevant labels:

```python
TONE_KEYWORDS = {
    "Frustrated": ["frustrated", "angry", "annoyed", "unacceptable", "ridiculous", ...],
    "Apologetic": ["sorry", "apologize", "apologies", "regret", ...],
    "Professional": ["certainly", "absolutely", "thank you for calling", ...],
    "Rushed": ["quick", "hurry", "as fast as", "just need", ...],
}
```

Why keywords instead of another ML model? Two reasons: (1) tone in call centers maps to specific vocabulary that's very domain-specific, and (2) it's transparent and debuggable -- managers can understand _why_ a call was flagged as "Frustrated" by looking at the keywords that matched, unlike a black-box model.

---

## API Design

The backend exposes four endpoints:

```
POST /analyze        Upload audio, run full pipeline, return report
GET  /results        List all results (optional date filters)
GET  /results/{id}   Fetch a specific result
GET  /               Health check
```

The `/analyze` endpoint is synchronous -- the client waits while all five pipeline stages run. For a typical 5-minute call with the `base` Whisper model, this takes 30-60 seconds. I chose synchronous over a task queue (like Celery) to keep the architecture simple. For production with heavy load, you'd want to make this async with a job queue and polling.

Error handling is layered. The audio normalization step catches FFmpeg-related failures and returns a helpful message telling users to install FFmpeg. The diarization and transcription steps have their own error handling that lets the pipeline degrade gracefully.

---

## The Dashboard

Streamlit was a deliberate choice over React or Vue. The entire frontend is a single 215-line Python file. No build step, no node_modules, no webpack config. For an internal tool, this is the right tradeoff -- I can iterate on the UI in minutes, and anyone on the team who knows Python can modify it.

The dashboard has two views:

**List View** -- shows all analysis results with date filters, sentiment badges, and tone labels. Each row shows the first two insight bullets as a preview.

**Detail View** -- full report with transcript, per-speaker breakdown, all insights, and an expandable segment-by-segment analysis showing timestamps, speakers, sentiment, and tone.

Navigation uses Streamlit's `query_params` -- clicking "View" on a result sets `?result_id=<uuid>` in the URL, which switches to the detail view. Simple, bookmarkable, no client-side routing library needed.

---

## Design Decisions I'd Make Differently

**File-based storage** works for prototyping but doesn't scale. The `list_results` function reads every JSON file in the results directory on every call. With thousands of results, this becomes slow. A SQLite database (or PostgreSQL for multi-user) would be the natural next step.

**Synchronous processing** means the API blocks during analysis. For production, I'd add a task queue (Celery + Redis) and return a job ID that the client polls for completion.

**No audio playback** in the dashboard. Being able to click on a segment and hear the audio would make the tool significantly more useful for QA reviewers. This would require serving audio files through the API and adding an HTML5 audio player to the Streamlit app.

**Keyword-based tone detection** is a good starting point but has obvious limitations. A fine-tuned classifier trained on actual call center data would be more accurate and handle nuance better.

---

## Running It Yourself

Prerequisites: Python 3.10+, FFmpeg.

```bash
cd "voice analyzer"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1: Start the API
uvicorn app.main:app --reload

# Terminal 2: Start the dashboard
streamlit run dashboard/streamlit_app.py
```

Open `http://localhost:8501`, upload a call recording, and watch the analysis run. No API keys needed -- everything runs on your machine.

For speaker diarization, you'll need a (free) Hugging Face token and to accept the pyannote model license. Set `HF_TOKEN` in your `.env` file.

---

## Tech Stack

- **Backend:** FastAPI + Uvicorn
- **Transcription:** OpenAI Whisper (local)
- **Sentiment:** HuggingFace Transformers (RoBERTa)
- **Diarization:** pyannote-audio
- **Audio Processing:** pydub + librosa + FFmpeg
- **ML Framework:** PyTorch
- **Dashboard:** Streamlit
- **Storage:** File-based JSON
- **Python:** 3.12

---

*The full source code is available on GitHub. Built as a weekend project that turned into something genuinely useful for understanding what happens in thousands of calls without listening to a single one.*
