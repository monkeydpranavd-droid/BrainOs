"""
app/storage/supabase_storage.py
─────────────────────────────────────────────────────────────────────────────
StorageService integrating with Supabase Storage.
Falls back dynamically to local filesystem storage if credentials are placeholder
or if connection is unauthorized (unblocking local developer environments).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from app.auth.supabase import get_supabase_admin
from app.core.config import settings
from app.core.exceptions import SupabaseError

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        try:
            self.client = get_supabase_admin()
        except Exception:
            self.client = None
        self.required_buckets = ["documents", "previews", "thumbnails"]
        self._ensure_buckets_exist()

    def _ensure_buckets_exist(self) -> None:
        """Verify that recommended storage buckets exist. If not, create them."""
        if not self.client or self._is_placeholder():
            logger.info("Using local filesystem fallback (bucket check skipped).")
            return

        try:
            buckets = self.client.storage.list_buckets()
            existing_bucket_names = [b.name for b in buckets]
            
            for bucket in self.required_buckets:
                if bucket not in existing_bucket_names:
                    logger.info("Bucket '%s' not found. Creating it...", bucket)
                    self.client.storage.create_bucket(bucket, options={"public": False})
        except Exception as e:
            logger.error("Failed to verify/create Supabase storage buckets: %s", e)

    def _is_placeholder(self) -> bool:
        key = settings.SUPABASE_SERVICE_ROLE_KEY
        return (
            not key
            or key.startswith("your-service-role")
            or "publishable" in key
        )

    def _upload_local(self, bucket: str, path: str, file_bytes: bytes) -> str:
        """Helper to write files to local uploads/ directory."""
        local_dir = Path(__file__).resolve().parent.parent.parent / "uploads" / bucket
        file_path = local_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            
        logger.info("Local storage fallback: saved file to %s", file_path)
        return path

    def upload_file(self, bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
        """
        Upload file bytes to a specified bucket.
        Returns the storage path on success. Falls back to local filesystem on failure.
        """
        if self._is_placeholder():
            return self._upload_local(bucket, path, file_bytes)

        try:
            self.client.storage.from_(bucket).upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            logger.info("Successfully uploaded file to Supabase storage: %s/%s", bucket, path)
            return path
        except Exception as e:
            logger.warning("Supabase Storage upload failed: %s. Falling back to local storage.", e)
            return self._upload_local(bucket, path, file_bytes)

    def download_file(self, bucket: str, path: str) -> bytes:
        """Download file bytes from specified bucket or local storage fallback."""
        local_path = Path(__file__).resolve().parent.parent.parent / "uploads" / bucket / path
        if local_path.exists():
            with open(local_path, "rb") as f:
                return f.read()

        if self._is_placeholder() or not self.client:
            raise SupabaseError("File not found in local storage fallback.")

        try:
            return self.client.storage.from_(bucket).download(path)
        except Exception as e:
            logger.error("Supabase Storage Download Error: %s", e)
            raise SupabaseError(f"Failed to download file from storage: {str(e)}")

    def delete_file(self, bucket: str, path: str) -> None:
        """Delete a file from the specified bucket or local storage fallback."""
        local_path = Path(__file__).resolve().parent.parent.parent / "uploads" / bucket / path
        if local_path.exists():
            try:
                local_path.unlink()
                logger.info("Local storage fallback: deleted file %s", local_path)
            except Exception:
                pass

        if self._is_placeholder() or not self.client:
            return

        try:
            self.client.storage.from_(bucket).remove([path])
            logger.info("Successfully deleted file from Supabase storage: %s/%s", bucket, path)
        except Exception as e:
            logger.error("Supabase Storage Delete Error: %s", e)
            raise SupabaseError(f"Failed to delete file from storage: {str(e)}")

    def signed_url(self, bucket: str, path: str, expires_in_seconds: int = 3600) -> str:
        """Generate secure signed URL or local preview URL fallback."""
        local_path = Path(__file__).resolve().parent.parent.parent / "uploads" / bucket / path
        if local_path.exists() or self._is_placeholder() or not self.client:
            return f"http://127.0.0.1:8000/api/v1/documents/local-preview?bucket={bucket}&path={path}"

        try:
            res = self.client.storage.from_(bucket).create_signed_url(path, expires_in_seconds)
            if isinstance(res, dict) and "signedURL" in res:
                return res["signedURL"]
            if hasattr(res, "get"):
                return res.get("signedURL") or str(res)
            return str(res)
        except Exception as e:
            logger.warning("Failed to generate Supabase signed URL: %s. Using local preview.", e)
            return f"http://127.0.0.1:8000/api/v1/documents/local-preview?bucket={bucket}&path={path}"
