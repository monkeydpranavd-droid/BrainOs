"""
app/documents/parser.py
─────────────────────────────────────────────────────────────────────────────
Document parsers using PyMuPDF, python-docx, python-pptx, and pandas.
Provides raw text extraction, page counts, and metadata dictionaries.
Compatible with Python 3.9.
"""

from __future__ import annotations

import io
import logging
from typing import Dict, Any, Tuple

import fitz          # PyMuPDF
import docx          # python-docx
import pptx          # python-pptx
import pandas as pd

logger = logging.getLogger(__name__)


def parse_pdf(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse PDF bytes using PyMuPDF."""
    text_content = []
    metadata = {}
    page_count = 0
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            page_count = doc.page_count
            metadata = doc.metadata or {}
            title = metadata.get("title") or ""
            
            for page in doc:
                text_content.append(page.get_text())
                
        full_text = "\n".join(text_content)
        return title, full_text, page_count, metadata
    except Exception as e:
        logger.error("Error parsing PDF: %s", e)
        raise ValueError(f"Failed to parse PDF document: {str(e)}")


def parse_docx(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse DOCX bytes using python-docx."""
    try:
        stream = io.BytesIO(file_bytes)
        doc = docx.Document(stream)
        
        paragraphs = [p.text for p in doc.paragraphs]
        # Include table cells if present
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)
                    
        full_text = "\n".join(paragraphs)
        
        # Read standard core properties
        metadata = {}
        title = ""
        try:
            props = doc.core_properties
            title = props.title or ""
            metadata = {
                "author": props.author or "",
                "created": str(props.created) if props.created else "",
                "modified": str(props.modified) if props.modified else "",
                "version": props.version or "",
            }
        except Exception:
            pass # Docx might lack core properties
            
        return title, full_text, 1, metadata
    except Exception as e:
        logger.error("Error parsing DOCX: %s", e)
        raise ValueError(f"Failed to parse DOCX document: {str(e)}")


def parse_pptx(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse PPTX bytes using python-pptx."""
    try:
        stream = io.BytesIO(file_bytes)
        prs = pptx.Presentation(stream)
        slides_text = []
        
        for slide in prs.slides:
            slide_parts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    slide_parts.append(shape.text)
            slides_text.append("\n".join(slide_parts))
            
        full_text = "\n--- Slide ---\n".join(slides_text)
        page_count = len(prs.slides)
        
        # Read properties
        title = ""
        metadata = {}
        try:
            props = prs.core_properties
            title = props.title or ""
            metadata = {
                "author": props.author or "",
                "created": str(props.created) if props.created else "",
                "modified": str(props.modified) if props.modified else "",
            }
        except Exception:
            pass
            
        return title, full_text, page_count, metadata
    except Exception as e:
        logger.error("Error parsing PPTX: %s", e)
        raise ValueError(f"Failed to parse PPTX presentation: {str(e)}")


def parse_csv(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse CSV bytes using pandas."""
    try:
        stream = io.BytesIO(file_bytes)
        df = pd.read_csv(stream)
        # Convert df to string/markdown
        markdown_text = df.to_markdown(index=False)
        metadata = {"columns": list(df.columns), "rows_count": len(df)}
        return "", markdown_text, 1, metadata
    except Exception as e:
        logger.error("Error parsing CSV: %s", e)
        raise ValueError(f"Failed to parse CSV file: {str(e)}")


def parse_txt(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse plain text bytes."""
    try:
        # Detect encoding safely
        for encoding in ["utf-8", "latin-1", "windows-1252"]:
            try:
                text = file_bytes.decode(encoding)
                # Estimate page count (roughly 3000 chars per page)
                page_count = max(1, len(text) // 3000)
                return "", text, page_count, {}
            except UnicodeDecodeError:
                continue
        raise ValueError("Failed to decode text file with standard encodings.")
    except Exception as e:
        logger.error("Error parsing TXT: %s", e)
        raise ValueError(f"Failed to parse TXT file: {str(e)}")


def parse_markdown(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse Markdown bytes."""
    # Markdown parses exactly like text in terms of extraction
    title, text_content, pages, meta = parse_txt(file_bytes)
    
    # Try to extract a title from the first H1 header (e.g., "# Title")
    for line in text_content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
            
    return title, text_content, pages, {"format": "markdown"}


def parse_image(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Placeholder image OCR parser."""
    ocr_placeholder_text = "[OCR Placeholder: Image content extraction will be performed here in future sprints.]"
    return "Image Upload", ocr_placeholder_text, 1, {"ocr_processed": False}


def get_parser_for_mime(mime_type: str):
    """Retrieve the appropriate parsing function for a given MIME type."""
    mime_map = {
        "application/pdf": parse_pdf,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": parse_pptx,
        "text/csv": parse_csv,
        "text/plain": parse_txt,
        "text/markdown": parse_markdown,
        "image/png": parse_image,
        "image/jpeg": parse_image,
        "image/jpg": parse_image,
        "image/gif": parse_image,
        "image/webp": parse_image,
    }
    
    # Check for text/plain fallbacks
    if mime_type.startswith("text/"):
        if "csv" in mime_type:
            return parse_csv
        if "markdown" in mime_type or "md" in mime_type:
            return parse_markdown
        return parse_txt
        
    if mime_type.startswith("image/"):
        return parse_image

    return mime_map.get(mime_type)
