"""
app/knowledge/chunking.py
─────────────────────────────────────────────────────────────────────────────
Chunking algorithm to segment parsed document text into retrieval window slices.
Prepares the data for Sprint 5 (vector storage and retrieval).
Compatible with Python 3.9.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any


def chunk_text(
    text: str,
    chunk_size_words: int = 400,
    chunk_overlap_words: int = 50,
) -> List[Dict[str, Any]]:
    """
    Split text into chunks based on word count with a sliding overlap window.
    Returns list of dicts: {"content": str, "token_count": int, "index": int}
    """
    if not text or not text.strip():
        return []

    # Clean whitespace and tokenize by word
    words = [w for w in re.split(r"\s+", text) if w]
    total_words = len(words)
    
    if total_words == 0:
        return []

    chunks = []
    chunk_index = 0
    start_idx = 0
    
    while start_idx < total_words:
        end_idx = min(start_idx + chunk_size_words, total_words)
        chunk_words = words[start_idx:end_idx]
        chunk_content = " ".join(chunk_words)
        
        # Approximate tokens (standard ratio: 1 word ~ 1.3 tokens)
        token_estimate = int(len(chunk_words) * 1.3)
        
        chunks.append({
            "content": chunk_content,
            "token_count": max(1, token_estimate),
            "chunk_index": chunk_index,
        })
        
        chunk_index += 1
        # Advance starting point by size minus overlap
        step = chunk_size_words - chunk_overlap_words
        if step <= 0:
            step = chunk_size_words
        start_idx += step
        
        # Guard to prevent infinite loop if end reached
        if end_idx == total_words:
            break
            
    return chunks
