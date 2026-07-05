"""
app/knowledge/chunking.py
─────────────────────────────────────────────────────────────────────────────
Ingestion chunker. Splits extracted text into slices of 1000 characters
with a 150 character overlap, preserving sentence boundaries where possible.
Compatible with Python 3.9.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any


def chunk_text(
    text: str,
    chunk_size_chars: int = 1000,
    chunk_overlap_chars: int = 150,
) -> List[Dict[str, Any]]:
    """
    Split text into character-based chunks with a sliding overlap.
    Averages 1000 characters per chunk, with 150 characters overlap.
    Optimizes for sentence boundaries (ends chunks at periods/newlines when possible).
    """
    if not text or not text.strip():
        return []

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text).strip()
    total_len = len(text)
    
    if total_len <= chunk_size_chars:
        # Fits in a single chunk
        return [{
            "content": text,
            "token_count": max(1, int(total_len / 4)), # Standard rough estimate: ~4 chars per token
            "chunk_index": 0
        }]

    chunks = []
    chunk_index = 0
    start_idx = 0

    while start_idx < total_len:
        end_idx = min(start_idx + chunk_size_chars, total_len)
        
        # Optimize boundary: look back up to 80 chars for a sentence/paragraph end (. or \n or ? or !)
        if end_idx < total_len:
            boundary_idx = -1
            lookback_limit = max(start_idx + chunk_size_chars - 80, start_idx + chunk_overlap_chars)
            for idx in range(end_idx - 1, lookback_limit - 1, -1):
                if text[idx] in (".", "\n", "?", "!"):
                    boundary_idx = idx + 1
                    break
            if boundary_idx != -1:
                end_idx = boundary_idx

        chunk_content = text[start_idx:end_idx].strip()
        
        # Skip empty chunks
        if chunk_content:
            token_estimate = max(1, int(len(chunk_content) / 4))
            chunks.append({
                "content": chunk_content,
                "token_count": token_estimate,
                "chunk_index": chunk_index
            })
            chunk_index += 1

        # Advance start_idx: next chunk starts at end_idx minus overlap
        next_start = end_idx - chunk_overlap_chars
        if next_start <= start_idx:
            # Ensure forward progress
            start_idx = end_idx
        else:
            start_idx = next_start

        if end_idx == total_len:
            break

    return chunks
