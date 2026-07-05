"""
app/documents/metadata.py
─────────────────────────────────────────────────────────────────────────────
Metadata extraction coordinator.
Aggregates summarization, classification, and entity extraction outputs.
Compatible with Python 3.9.
"""

from __future__ import annotations

from typing import Dict, Any

from app.knowledge.summarizer import summarize_text
from app.knowledge.classifier import classify_text
from app.knowledge.entities import extract_entities_from_text


def extract_metadata_from_raw_text(text: str) -> Dict[str, Any]:
    """Analyze document text and return aggregated structural metadata."""
    if not text or not text.strip():
        return {
            "summary": "",
            "topics": [],
            "language": "en",
            "entities": {
                "people": [],
                "technologies": [],
                "projects": [],
                "dates": [],
                "departments": [],
            }
        }

    # 1. Summary Heuristic
    summary = summarize_text(text)

    # 2. Classifier (Topics)
    topics = classify_text(text)

    # 3. Entities
    entities = extract_entities_from_text(text)

    # 4. Language detection (heuristic fallback)
    # Default to english for standard document processing pipeline
    language = "en"
    if "bonjour" in text.lower() or "merci" in text.lower():
        language = "fr"
    elif "hola" in text.lower() or "gracias" in text.lower():
        language = "es"

    return {
        "summary": summary,
        "topics": topics,
        "language": language,
        "entities": entities,
    }
