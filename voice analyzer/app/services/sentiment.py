"""Sentiment and tone analysis on transcript text."""
import re
from typing import Any

from app.config import SENTIMENT_MODEL

# Tone keywords for call-center-relevant labels (heuristics on top of sentiment)
TONE_KEYWORDS = {
    "Frustrated": [
        "frustrated", "angry", "annoyed", "unacceptable", "ridiculous",
        "terrible", "worst", "never again", "complaint", "disappointed",
    ],
    "Apologetic": [
        "sorry", "apologize", "apologies", "regret", "unfortunate",
        "mistake", "my fault", "we apologize",
    ],
    "Professional": [
        "certainly", "absolutely", "thank you for calling", "how may I help",
        "I understand", "I'd be happy to", "please", "appreciate",
    ],
    "Rushed": [
        "quick", "hurry", "as fast as", "just need", "gotta go",
        "have to go", "in a rush", "short on time",
    ],
}


def _load_sentiment_pipeline():
    from transformers import pipeline
    return pipeline(
        "sentiment-analysis",
        model=SENTIMENT_MODEL,
        top_k=None,
    )


# Lazy singleton to avoid loading model on import
_sentiment_pipeline = None


def _get_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = _load_sentiment_pipeline()
    return _sentiment_pipeline


def analyze_sentiment(text: str) -> dict[str, Any]:
    """
    Run sentiment on text. Returns label (positive/negative/neutral) and scores.
    """
    if not (text or "").strip():
        return {"label": "neutral", "score": 0.0, "scores": {}}

    text_clean = text.strip()[:512]  # model max length
    pipe = _get_pipeline()
    out = pipe(text_clean)[0]
    # out is list of {"label": "positive"|"negative"|"neutral", "score": float}
    if isinstance(out, list):
        scores = {x["label"].lower(): x["score"] for x in out}
        label = max(scores, key=scores.get)
        score = scores[label]
    else:
        scores = {out["label"].lower(): out["score"]}
        label = out["label"].lower()
        score = out["score"]

    return {"label": label, "score": float(score), "scores": scores}


def infer_tone(text: str) -> str:
    """
    Infer call-center tone from keywords. Returns one of:
    Professional, Frustrated, Apologetic, Neutral, Rushed.
    """
    if not (text or "").strip():
        return "Neutral"

    lower = text.lower()
    scores = {}

    for tone, keywords in TONE_KEYWORDS.items():
        count = sum(1 for k in keywords if k in lower)
        if count > 0:
            scores[tone] = count

    if not scores:
        return "Neutral"
    return max(scores, key=scores.get)


def analyze_segment(segment_text: str) -> dict[str, Any]:
    """Sentiment + tone for one segment."""
    sentiment = analyze_sentiment(segment_text)
    tone = infer_tone(segment_text)
    return {
        "sentiment": sentiment["label"],
        "sentiment_score": sentiment["score"],
        "tone": tone,
        "scores": sentiment.get("scores", {}),
    }


def analyze_full_transcript(
    full_text: str,
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Analyze full transcript and optionally per-segment. Returns:
    - overall: sentiment + tone for full text
    - segment_analyses: list of per-segment sentiment/tone (if segments provided)
    - overall_sentiment_label, overall_tone, insight bullets
    """
    overall_sentiment = analyze_sentiment(full_text)
    overall_tone = infer_tone(full_text)

    segment_analyses = []
    if segments:
        for seg in segments:
            text = seg.get("text") or ""
            seg_analysis = analyze_segment(text)
            entry = {
                "start": seg.get("start"),
                "end": seg.get("end"),
                "text": text[:200] + ("..." if len(text) > 200 else ""),
                **seg_analysis,
            }
            if seg.get("speaker") is not None:
                entry["speaker"] = seg["speaker"]
            segment_analyses.append(entry)

    # Per-speaker aggregation when segments have speaker labels
    by_speaker: dict[str, dict[str, Any]] = {}
    if segment_analyses and any(a.get("speaker") for a in segment_analyses):
        from collections import defaultdict
        texts_by_speaker: dict[str, list[str]] = defaultdict(list)
        for a in segment_analyses:
            sp = a.get("speaker")
            if sp and a.get("text"):
                texts_by_speaker[sp].append(a["text"].rstrip("..."))
        for speaker, texts in texts_by_speaker.items():
            combined = " ".join(texts).strip()
            if not combined:
                continue
            sent = analyze_sentiment(combined)
            tone = infer_tone(combined)
            by_speaker[speaker] = {
                "sentiment": sent["label"],
                "sentiment_score": sent["score"],
                "tone": tone,
            }

    # Build 2–3 insight bullets
    insights = _build_insights(
        full_text,
        overall_sentiment,
        overall_tone,
        segment_analyses,
        by_speaker,
    )

    result = {
        "overall_sentiment": overall_sentiment["label"],
        "overall_sentiment_score": overall_sentiment["score"],
        "overall_sentiment_scores": overall_sentiment.get("scores", {}),
        "overall_tone": overall_tone,
        "segment_analyses": segment_analyses,
        "insights": insights,
    }
    if by_speaker:
        result["by_speaker"] = by_speaker
    return result


def _build_insights(
    full_text: str,
    overall_sentiment: dict,
    overall_tone: str,
    segment_analyses: list[dict],
    by_speaker: dict | None = None,
) -> list[str]:
    """Generate 2–3 short insight bullets for managers."""
    insights = []
    by_speaker = by_speaker or {}

    label = overall_sentiment.get("label", "neutral")
    score = overall_sentiment.get("score", 0)

    if label == "positive" and score > 0.8:
        insights.append("Overall customer sentiment was clearly positive.")
    elif label == "negative":
        insights.append("Overall sentiment was negative; consider follow-up or coaching.")
    else:
        insights.append(f"Overall sentiment: {label}; tone perceived as {overall_tone}.")

    if by_speaker:
        for sp, data in by_speaker.items():
            st = data.get("tone", "")
            if st == "Frustrated":
                insights.append(f"{sp} showed frustrated tone; review handling.")
                break
        for sp, data in by_speaker.items():
            if data.get("tone") == "Professional":
                insights.append(f"{sp} maintained professional tone.")
                break
    else:
        if overall_tone == "Professional":
            insights.append("Agent/caller tone remained professional throughout.")
        elif overall_tone == "Frustrated":
            insights.append("Frustration detected in the conversation; review handling and escalation.")

    if segment_analyses:
        tones = [a.get("tone") for a in segment_analyses if a.get("tone")]
        if tones and len(set(tones)) > 1:
            insights.append("Tone varied across the call; mid-call or closing tone may need attention.")

    return insights[:3]
