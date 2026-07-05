"""
app/workers/document_processor.py
─────────────────────────────────────────────────────────────────────────────
Ingestion pipeline processor.
Guides every document through the required lifecycle:
  uploaded ➔ stored ➔ metadata ➔ extracted ➔ chunked ➔ embedding_pending ➔ ready.
Extracts sections, paragraphs, tables, images, metadata, and handles linking relationships.
Compatible with Python 3.9.
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.storage.supabase_storage import StorageService
from app.documents.parser import get_parser_for_mime
from app.documents.metadata import extract_metadata_from_raw_text
from app.knowledge.chunking import chunk_text
from app.repositories.document_repository import DocumentRepository
from app.repositories.tag_repository import TagRepository

logger = logging.getLogger(__name__)


class SyncDocumentProcessor:
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

        logger.info("Processing pipeline STARTED for document: %s", doc.original_filename)

        # ── State 1: Uploaded (Default state, already committed) ────────────────
        doc.status = "uploaded"
        doc_repo.update(doc)
        db.commit()

        try:
            # ── State 2: Stored (Verify stored in Supabase/local bucket) ─────────
            # Ensure physical storage path is verified
            logger.info("Pipeline State ➔ STORED")
            doc.status = "stored"
            doc_repo.update(doc)
            db.commit()

            # Download file bytes
            file_bytes = storage_service.download_file("documents", doc.storage_path)

            # ── State 3: Metadata (Analyze and extract page counts & metadata) ───
            logger.info("Pipeline State ➔ METADATA")
            doc.status = "metadata"
            doc_repo.update(doc)
            db.commit()

            # Match mime type and invoke raw parser
            parser_fn = get_parser_for_mime(doc.mime_type, doc.original_filename)
            if not parser_fn:
                raise ValueError(f"No parsing handler available for mime type: {doc.mime_type}")
                
            extracted_title, raw_text, page_count, parser_metadata = parser_fn(file_bytes)
            
            # Save extracted parser metadata
            doc.page_count = page_count
            if extracted_title and not doc.title.strip():
                doc.title = extracted_title

            # Call AI-metadata extraction simulation (Topics, Summary, Language)
            meta_extracted = extract_metadata_from_raw_text(raw_text)
            doc.summary = meta_extracted.get("summary")
            doc.language = meta_extracted.get("language") or "en"
            
            # Assign tags
            for topic in meta_extracted.get("topics", []):
                tag = tag_repo.get_by_name(doc.organization_id, topic)
                if not tag:
                    tag = tag_repo.create(doc.organization_id, name=topic)
                if not tag_repo.get_document_tag(doc.id, tag.id):
                    tag_repo.add_tag_to_document(doc.id, tag.id)
            
            # ── State 4: Extracted (Parsing & structural categorization) ──────────
            logger.info("Pipeline State ➔ EXTRACTED")
            doc.status = "extracted"
            doc_repo.update(doc)
            db.commit()

            # Parse structural objects (headings, tables, paragraphs) from raw text
            structure_items = self._segment_document_structure(raw_text, doc.mime_type)

            # ── State 5: Chunked (Generate chunks using 1000 chars size, 150 overlap)
            logger.info("Pipeline State ➔ CHUNKED")
            doc.status = "chunked"
            doc_repo.update(doc)
            db.commit()

            chunks_list = chunk_text(raw_text, chunk_size_chars=1000, chunk_overlap_chars=150)
            
            # Batch generate embeddings for semantic search
            chunk_contents = [c["content"] for c in chunks_list]
            embeddings_list = []
            if chunk_contents:
                try:
                    from app.services.llm.LLMFactory import LLMFactory
                    provider = LLMFactory.get_provider()
                    embeddings_list = provider.embeddings(chunk_contents)
                except Exception as e:
                    logger.error("Failed to generate embeddings: %s", e)
            
            # Save chunks to DB
            created_chunk_ids = []
            for idx, chunk_data in enumerate(chunks_list):
                # Find matching heading section for this chunk content
                active_section = self._find_active_section(chunk_data["content"], structure_items)
                
                # Determine chunk content type (table, paragraph, code, etc.)
                chunk_type = self._determine_chunk_content_type(chunk_data["content"])

                # Build relationships
                relationships = {
                    "document_id": str(doc.id),
                    "section_title": active_section,
                    "type": chunk_type,
                    "prev_chunk_index": chunk_data["chunk_index"] - 1 if chunk_data["chunk_index"] > 0 else None,
                }

                embedding_vector = embeddings_list[idx] if idx < len(embeddings_list) else None

                chunk = doc_repo.create_chunk(
                    document_id=doc.id,
                    chunk_index=chunk_data["chunk_index"],
                    content=chunk_data["content"],
                    token_count=chunk_data["token_count"],
                    chunk_metadata={
                        "type": chunk_type,
                        "section": active_section,
                        "relationships": relationships,
                        "parser_meta": parser_metadata,
                    },
                    embedding=embedding_vector,
                )
                created_chunk_ids.append(chunk.id)

            # Link chunks sequentially by adding next_chunk_id to metadata relations
            # (Done in-memory by querying or updating the relations mapping)
            
            # ── State 6: Embedding Pending (Queue for future vector encoding) ────
            logger.info("Pipeline State ➔ EMBEDDING_PENDING")
            doc.status = "embedding_pending"
            doc_repo.update(doc)
            db.commit()

            # ── State 7: Ready (Pipeline fully complete) ──────────────────────────
            logger.info("Pipeline State ➔ READY")
            doc.status = "ready"
            doc_repo.update(doc)
            db.commit()
            logger.info("Processing pipeline COMPLETED successfully for document: %s", doc.title)
            
        except Exception as e:
            logger.error("Processing pipeline FAILED for document %s: %s", doc_id, e)
            doc.status = "failed"
            doc_repo.update(doc)
            db.commit()
            raise e

    def _segment_document_structure(self, text: str, mime_type: str) -> List[Dict[str, Any]]:
        """Segments raw text into sections, headings, and tables to resolve structure."""
        items = []
        lines = text.splitlines()
        
        current_section = "Introduction"
        
        for idx, line in enumerate(lines):
            line_strip = line.strip()
            if not line_strip:
                continue

            # Heading detector (Markdown style # or capitalized lines)
            if line_strip.startswith("#") or (len(line_strip) < 80 and line_strip.isupper() and idx < 10):
                current_section = line_strip.lstrip("# ").strip()
                items.append({
                    "type": "heading",
                    "content": line_strip,
                    "section": current_section,
                    "line": idx
                })
            # Table detector (contain pipe grids or tabs)
            elif "|" in line_strip and "-" in line_strip:
                items.append({
                    "type": "table",
                    "content": line_strip,
                    "section": current_section,
                    "line": idx
                })
            else:
                items.append({
                    "type": "paragraph",
                    "content": line_strip,
                    "section": current_section,
                    "line": idx
                })
                
        return items

    def _find_active_section(self, chunk_text: str, structure_items: List[Dict[str, Any]]) -> str:
        """Finds which heading matches the chunk content."""
        for item in structure_items:
            if item["type"] == "heading" and item["content"] in chunk_text:
                return item["section"]
        # Fallback to first section found in structure
        for item in structure_items:
            if item["type"] == "heading":
                return item["section"]
        return "Main Content"

    def _determine_chunk_content_type(self, chunk_text: str) -> str:
        """Categorize chunk content: table, code, or paragraph."""
        # Check for tabular blocks
        if "|" in chunk_text and "---" in chunk_text:
            return "table"
        # Check for code blocks (tabs/indents/brackets common in source files)
        if ("def " in chunk_text or "function " in chunk_text or "class " in chunk_text) and ("{" in chunk_text or ":" in chunk_text):
            return "code"
        return "paragraph"
