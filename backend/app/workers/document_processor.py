"""
app/workers/document_processor.py
─────────────────────────────────────────────────────────────────────────────
Background document processing pipeline worker interface.
Supports FastAPI BackgroundTasks or future Celery/n8n scaling.
Compatible with Python 3.9.
"""

from __future__ import annotations

import abc
import logging
import uuid

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.storage.supabase_storage import StorageService
from app.documents.parser import get_parser_for_mime
from app.documents.metadata import extract_metadata_from_raw_text
from app.knowledge.chunking import chunk_text
from app.repositories.document_repository import DocumentRepository
from app.repositories.tag_repository import TagRepository

logger = logging.getLogger(__name__)


class DocumentProcessorInterface(abc.ABC):
    @abc.abstractmethod
    def process_document(self, doc_id: uuid.UUID) -> None:
        """Execute document parsing, metadata extraction, and text chunking."""
        pass


class SyncDocumentProcessor(DocumentProcessorInterface):
    """
    Synchronous processing executor.
    Can be run immediately or delegated to a background thread / task executor.
    """

    def process_document(self, doc_id: uuid.UUID) -> None:
        # Run inside isolated DB session
        db = SessionLocal()
        try:
            self._execute_pipeline(db, doc_id)
        except Exception as e:
            logger.error("Failed executing document processing task for ID %s: %s", doc_id, e)
        finally:
            db.close()

    def _execute_pipeline(self, db: Session, doc_id: uuid.UUID) -> None:
        doc_repo = DocumentRepository(db)
        tag_repo = TagRepository(db)
        storage_service = StorageService()
        
        doc = doc_repo.get_by_id(doc_id)
        if not doc:
            logger.error("Document ID %s not found in DB.", doc_id)
            return

        logger.info("Processing pipeline STARTED for document: %s (Mime: %s)", doc.title, doc.mime_type)
        doc.status = "processing"
        doc_repo.update(doc)
        db.commit()

        try:
            # 1. Download file bytes from Supabase storage
            file_bytes = storage_service.download_file("documents", doc.storage_path)
            
            # 2. Match mime type and invoke raw parser
            parser_fn = get_parser_for_mime(doc.mime_type)
            if not parser_fn:
                raise ValueError(f"No parsing handler available for mime type: {doc.mime_type}")
                
            extracted_title, raw_text, page_count, parser_metadata = parser_fn(file_bytes)
            
            # Update page count
            doc.page_count = page_count
            if extracted_title and not doc.title.strip():
                doc.title = extracted_title

            # 3. Extract high-level metadata (Summary, topics, entities, language)
            extracted = extract_metadata_from_raw_text(raw_text)
            
            doc.summary = extracted["summary"]
            doc.language = extracted["language"]
            
            # 4. Generate & assign tags from detected topics
            for topic in extracted["topics"]:
                # Get or create tag
                tag = tag_repo.get_by_name(doc.organization_id, topic)
                if not tag:
                    tag = tag_repo.create(doc.organization_id, name=topic)
                
                # Assign tag to document if not already assigned
                if not tag_repo.get_document_tag(doc.id, tag.id):
                    tag_repo.add_tag_to_document(doc.id, tag.id)
            
            # 5. Chunk text content
            chunks = chunk_text(raw_text)
            for chunk_data in chunks:
                doc_repo.create_chunk(
                    document_id=doc.id,
                    chunk_index=chunk_data["chunk_index"],
                    content=chunk_data["content"],
                    token_count=chunk_data["token_count"],
                    chunk_metadata={"source": "parser", "pages": page_count},
                )
                
            doc.status = "processed"
            doc_repo.update(doc)
            db.commit()
            logger.info("Processing pipeline COMPLETED successfully for document: %s", doc.title)
            
        except Exception as e:
            logger.error("Processing pipeline FAILED for document %s: %s", doc_id, e)
            doc.status = "failed"
            doc_repo.update(doc)
            db.commit()
            raise e
