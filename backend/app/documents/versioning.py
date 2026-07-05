"""
app/documents/versioning.py
─────────────────────────────────────────────────────────────────────────────
Document versioning helpers to handle identical files and revisions.
Compatible with Python 3.9.
"""

from __future__ import annotations

import hashlib


def calculate_sha256(file_bytes: bytes) -> str:
    """Calculate SHA-256 checksum of file bytes to verify uniqueness."""
    sha256_hash = hashlib.sha256()
    # Read in chunks of 4KB to save memory on large files
    for i in range(0, len(file_bytes), 4096):
        sha256_hash.update(file_bytes[i:i+4096])
    return sha256_hash.hexdigest()
