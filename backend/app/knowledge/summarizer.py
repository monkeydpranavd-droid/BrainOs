"""
app/knowledge/summarizer.py
─────────────────────────────────────────────────────────────────────────────
Concise text summarizer heuristic.
Extracts significant opening sentences to build a readable document summary.
Compatible with Python 3.9.
"""

from __future__ import annotations

import re


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Extract a concise heuristic summary of the text."""
    if not text or not text.strip():
        return "Empty document."

    # Remove headers or system marks from top
    cleaned = re.sub(r"#+.*", "", text)
    cleaned = re.sub(r"\[.*?\]", "", cleaned)
    cleaned = " ".join(cleaned.split())

    # Split into sentences using crude boundaries
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return cleaned[:200] + "..." if len(cleaned) > 200 else cleaned

    summary_sentences = sentences[:max_sentences]
    summary = " ".join(summary_sentences)
    
    if len(summary) > 400:
        summary = summary[:397] + "..."
        
    return summary
