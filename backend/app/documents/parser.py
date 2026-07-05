"""
app/documents/parser.py
─────────────────────────────────────────────────────────────────────────────
Document parsers using PyMuPDF, python-docx, python-pptx, pandas, Pillow, and zipfile.
Provides raw text extraction, page counts, and metadata dictionaries.
Compatible with Python 3.9.
"""

from __future__ import annotations

import io
import re
import zipfile
import wave
import logging
from typing import Dict, Any, Tuple, Optional

import fitz          # PyMuPDF
import docx          # python-docx
import pptx          # python-pptx
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)


# ── PDF Parser ────────────────────────────────────────────────────────────────

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
        return title, full_text, page_count, {
            "title": title,
            "author": metadata.get("author") or "",
            "language": metadata.get("language") or "en",
            "keywords": metadata.get("keywords") or "",
            "creation_date": metadata.get("creationDate") or "",
            "mod_date": metadata.get("modDate") or "",
            "creator": metadata.get("creator") or "",
            "producer": metadata.get("producer") or ""
        }
    except Exception as e:
        logger.error("Error parsing PDF: %s", e)
        raise ValueError(f"Failed to parse PDF document: {str(e)}")


# ── DOCX / DOC Parser ─────────────────────────────────────────────────────────

def parse_docx(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse DOCX bytes using python-docx."""
    try:
        stream = io.BytesIO(file_bytes)
        doc = docx.Document(stream)
        
        paragraphs = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)
                    
        full_text = "\n".join(paragraphs)
        
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
            pass
            
        return title, full_text, 1, metadata
    except Exception as e:
        logger.error("Error parsing DOCX: %s", e)
        raise ValueError(f"Failed to parse DOCX document: {str(e)}")


# ── PPTX / PPT Parser ─────────────────────────────────────────────────────────

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


# ── Spreadsheet Parsers (CSV, XLS, XLSX) ──────────────────────────────────────

def parse_csv(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse CSV bytes using pandas."""
    try:
        stream = io.BytesIO(file_bytes)
        df = pd.read_csv(stream)
        markdown_text = df.to_markdown(index=False)
        metadata = {
            "columns": list(df.columns),
            "rows_count": len(df),
            "columns_count": len(df.columns)
        }
        return "", markdown_text, 1, metadata
    except Exception as e:
        logger.error("Error parsing CSV: %s", e)
        raise ValueError(f"Failed to parse CSV file: {str(e)}")


def parse_xlsx(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse XLSX / XLS Excel spreadsheets using pandas."""
    try:
        stream = io.BytesIO(file_bytes)
        excel_file = pd.ExcelFile(stream)
        sheet_texts = []
        metadata = {
            "sheets": excel_file.sheet_names,
            "total_sheets": len(excel_file.sheet_names)
        }
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            markdown_text = df.to_markdown(index=False)
            sheet_texts.append(f"### Sheet: {sheet_name}\n\n{markdown_text}")
        full_text = "\n\n".join(sheet_texts)
        return "", full_text, len(excel_file.sheet_names), metadata
    except Exception as e:
        logger.error("Error parsing Excel file: %s", e)
        raise ValueError(f"Failed to parse Excel file: {str(e)}")


# ── Plain Text & Markdown ─────────────────────────────────────────────────────

def parse_txt(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Parse plain text / code bytes with encoding fallbacks."""
    try:
        for encoding in ["utf-8", "latin-1", "windows-1252"]:
            try:
                text = file_bytes.decode(encoding)
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
    title, text_content, pages, meta = parse_txt(file_bytes)
    for line in text_content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, text_content, pages, {"format": "markdown"}


# ── RTF (Rich Text Format) Parser ─────────────────────────────────────────────

def parse_rtf(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Ingest Rich Text Format file by stripping controls."""
    try:
        text = file_bytes.decode("ascii", errors="ignore")
        clean_text = []
        in_control = False
        control_word = []
        for char in text:
            if char == "\\":
                in_control = True
                control_word = []
            elif in_control:
                if char.isalpha() or char.isdigit() or char == "-":
                    control_word.append(char)
                else:
                    in_control = False
                    if char != " ":
                        clean_text.append(char)
            elif char in ("{", "}"):
                continue
            else:
                clean_text.append(char)
        result = "".join(clean_text)
        result = re.sub(r"\n+", "\n", result)
        result = re.sub(r" +", " ", result).strip()
        return "", result, max(1, len(result) // 3000), {"format": "rtf"}
    except Exception as e:
        logger.error("Error parsing RTF: %s", e)
        return "", "", 1, {}


# ── Image Parser (PIL EXIF) ───────────────────────────────────────────────────

def parse_image(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
    """Extract image resolution, mode, and EXIF tags."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
        format_name = img.format or "Unknown"
        mode = img.mode
        
        info_lines = [
            f"Image Visual Asset Profile",
            f"Format: {format_name}",
            f"Dimensions: {width}x{height} pixels",
            f"Color Mode: {mode}"
        ]
        
        metadata = {
            "width": width,
            "height": height,
            "format": format_name,
            "mode": mode,
            "has_exif": bool(img.info.get("exif")),
        }
        
        try:
            exif_data = img.getexif()
            if exif_data:
                exif_dict = {}
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if isinstance(value, (str, int, float)):
                        exif_dict[str(tag_name)] = str(value)
                if exif_dict:
                    metadata["exif"] = exif_dict
                    info_lines.append("EXIF Metadata:")
                    for k, v in exif_dict.items():
                        info_lines.append(f"  {k}: {v}")
        except Exception:
            pass
            
        full_text = "\n".join(info_lines)
        return "Image Metadata", full_text, 1, metadata
    except Exception as e:
        logger.error("Error parsing image: %s", e)
        raise ValueError(f"Failed to parse image file: {str(e)}")


# ── Audio & Video Containers Pure-Python Parsers ──────────────────────────────

def parse_audio_wav(file_bytes: bytes) -> Dict[str, Any]:
    """Parse WAV headers using stdlib wave."""
    try:
        with wave.open(io.BytesIO(file_bytes), "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate) if rate else 0.0
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            bitrate = rate * channels * sample_width * 8
            return {
                "duration": duration,
                "codec": f"PCM {sample_width * 8}-bit",
                "bitrate": bitrate
            }
    except Exception:
        return {}


def parse_audio_mp3(file_bytes: bytes) -> Dict[str, Any]:
    """Pure-Python MP3 header frame scanner to fetch samplerate, bitrate, and duration."""
    sr_table = [
        [44100, 48000, 32000],
        [22050, 24000, 16000],
        [11025, 12000, 8000]
    ]
    br_table = [
        [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
        [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]
    ]
    for i in range(min(len(file_bytes) - 4, 32768)):
        if file_bytes[i] == 0xFF and (file_bytes[i+1] & 0xE0) == 0xE0:
            b1 = file_bytes[i+1]
            b2 = file_bytes[i+2]
            version = (b1 >> 3) & 0x03
            br_idx = (b2 >> 4) & 0x0F
            sr_idx = (b2 >> 2) & 0x03
            
            ver_idx = 0 if version == 3 else (1 if version == 2 else 2)
            try:
                samplerate = sr_table[ver_idx][sr_idx]
                bitrate = br_table[0 if ver_idx == 0 else 1][br_idx] * 1000
                duration = (len(file_bytes) * 8) / float(bitrate) if bitrate else 0.0
                return {
                    "duration": duration,
                    "codec": "MP3 Audio",
                    "bitrate": bitrate,
                    "sample_rate": samplerate
                }
            except Exception:
                pass
    return {"duration": 0.0, "codec": "MP3", "bitrate": 128000}


def parse_mp4_container(file_bytes: bytes) -> Dict[str, Any]:
    """Parse MP4/M4A/MOV container atoms for duration, resolution and codecs."""
    idx = 0
    limit = len(file_bytes)
    meta = {"duration": 0.0, "codec": "MPEG-4 Base Media"}
    while idx < limit - 8:
        try:
            size = int.from_bytes(file_bytes[idx:idx+4], "big")
            box_type = file_bytes[idx+4:idx+8].decode("ascii", errors="ignore")
            if size <= 0:
                break
            
            if box_type == "moov":
                idx += 8
                continue
            elif box_type == "mvhd":
                version = file_bytes[idx+8]
                timescale_start = idx + 8 + 4 + (16 if version == 1 else 8)
                timescale = int.from_bytes(file_bytes[timescale_start:timescale_start+4], "big")
                duration_bytes = 8 if version == 1 else 4
                duration_raw = int.from_bytes(file_bytes[timescale_start+4:timescale_start+4+duration_bytes], "big")
                if timescale > 0:
                    meta["duration"] = duration_raw / float(timescale)
                idx += size
                continue
            elif box_type == "trak":
                idx += 8
                continue
            elif box_type == "tkhd":
                version = file_bytes[idx+8]
                offset = 8 + 4 + (24 if version == 1 else 12)
                w_raw = int.from_bytes(file_bytes[idx+offset:idx+offset+4], "big") >> 16
                h_raw = int.from_bytes(file_bytes[idx+offset+4:idx+offset+8], "big") >> 16
                if w_raw > 0 and h_raw > 0:
                    meta["width"] = w_raw
                    meta["height"] = h_raw
                idx += size
                continue
            
            idx += size
        except Exception:
            break
    return meta


def parse_video_avi(file_bytes: bytes) -> Dict[str, Any]:
    """Parse AVI headers to extract frame sizes and rates."""
    idx = file_bytes.find(b"avih")
    if idx != -1:
        try:
            us_per_frame = int.from_bytes(file_bytes[idx+8:idx+12], "little")
            total_frames = int.from_bytes(file_bytes[idx+24:idx+28], "little")
            width = int.from_bytes(file_bytes[idx+40:idx+44], "little")
            height = int.from_bytes(file_bytes[idx+44:idx+48], "little")
            fps = 1000000.0 / us_per_frame if us_per_frame else 24.0
            duration = (total_frames * us_per_frame) / 1000000.0
            return {
                "duration": duration,
                "fps": fps,
                "width": width,
                "height": height,
                "codec": "AVI Container"
            }
        except Exception:
            pass
    return {"duration": 0.0, "fps": 24.0, "width": 640, "height": 480, "codec": "AVI"}


def parse_media_asset(file_bytes: bytes, filename: str, mime_type: str) -> Tuple[str, str, int, Dict[str, Any]]:
    """Central parser for Audio, Video, and Archive files."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    meta = {"filename": filename, "mime_type": mime_type, "file_size_bytes": len(file_bytes)}
    
    # 1. Archive
    if ext == "zip":
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                names = z.namelist()
                meta["files"] = names
                meta["total_files"] = len(names)
                summary = f"ZIP File: contains {len(names)} files.\nFiles:\n" + "\n".join(f" - {f}" for f in names[:15])
                if len(names) > 15:
                    summary += f"\n ... and {len(names)-15} more files."
                return f"Archive: {filename}", summary, 1, meta
        except Exception as e:
            return filename, f"Corrupted Zip: {e}", 1, meta
            
    # 2. Audio
    if ext in ("wav", "mp3", "m4a"):
        audio_info = {}
        if ext == "wav":
            audio_info = parse_audio_wav(file_bytes)
        elif ext == "mp3":
            audio_info = parse_audio_mp3(file_bytes)
        elif ext == "m4a":
            audio_info = parse_mp4_container(file_bytes)
            
        duration = audio_info.get("duration", 0.0)
        codec = audio_info.get("codec", "Audio")
        bitrate = audio_info.get("bitrate", 128000)
        meta.update({"duration": duration, "codec": codec, "bitrate": bitrate})
        
        summary = (
            f"Audio Asset Ingested:\n"
            f"Codec: {codec}\n"
            f"Duration: {duration:.2f} seconds\n"
            f"Bitrate: {bitrate / 1000:.0f} kbps"
        )
        return f"Audio: {filename}", summary, 1, meta

    # 3. Video
    if ext in ("mp4", "mov", "avi"):
        video_info = {}
        if ext in ("mp4", "mov"):
            video_info = parse_mp4_container(file_bytes)
        elif ext == "avi":
            video_info = parse_video_avi(file_bytes)
            
        duration = video_info.get("duration", 0.0)
        width = video_info.get("width", 1920)
        height = video_info.get("height", 1080)
        fps = video_info.get("fps", 24.0)
        codec = video_info.get("codec", "Video")
        meta.update({"duration": duration, "width": width, "height": height, "fps": fps, "codec": codec})
        
        summary = (
            f"Video Asset Ingested:\n"
            f"Resolution: {width}x{height}\n"
            f"FPS: {fps:.2f}\n"
            f"Duration: {duration:.2f} seconds\n"
            f"Codec: {codec}"
        )
        return f"Video: {filename}", summary, 1, meta

    return parse_binary_fallback(file_bytes, filename, mime_type)


def parse_binary_fallback(file_bytes: bytes, filename: str, mime_type: str) -> Tuple[str, str, int, Dict[str, Any]]:
    """Fallback block for all unrecognized files."""
    file_size_mb = len(file_bytes) / (1024 * 1024)
    file_summary = (
        f"Ingested Binary Resource:\n"
        f"File name: {filename}\n"
        f"Type: {mime_type}\n"
        f"Size: {file_size_mb:.3f} MB\n"
        f"[Metadata extracted successfully]"
    )
    metadata = {
        "filename": filename,
        "mime_type": mime_type,
        "file_size_bytes": len(file_bytes),
        "indexing_mode": "metadata_only"
    }
    return f"Binary: {filename}", file_summary, 1, metadata


# ── MIME / Extension Mapper ───────────────────────────────────────────────────

def get_parser_for_mime(mime_type: str, filename: Optional[str] = None):
    """Resolve correct parsing handler for any file type/extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if filename and "." in filename else ""

    # Extensions override
    if ext in ("md", "markdown"):
        return parse_markdown
    if ext in ("csv",):
        return parse_csv
    if ext in ("xlsx", "xls"):
        return parse_xlsx
    if ext in ("pdf",):
        return parse_pdf
    if ext in ("docx", "doc"):
        return parse_docx
    if ext in ("pptx", "ppt"):
        return parse_pptx
    if ext in ("png", "jpg", "jpeg", "webp", "gif", "svg"):
        return parse_image
    if ext in ("rtf",):
        return parse_rtf
    
    # Text / Code source formats
    text_extensions = {
        "py", "js", "ts", "java", "c", "cpp", "h", "hpp", "go", "rs", "swift", "kt",
        "php", "sql", "yaml", "yml", "dockerfile", "json", "xml", "html", "htm",
        "ini", "conf", "sh", "bat"
    }
    if ext in text_extensions:
        return parse_txt

    # Archives / Media assets
    media_extensions = {
        "zip", "rar", "tar", "gz", "7z",
        "mp3", "wav", "m4a", "ogg", "flac",
        "mp4", "mov", "avi", "mkv", "webm", "mpeg"
    }
    if ext in media_extensions:
        return lambda fb: parse_media_asset(fb, filename or "asset", mime_type)

    # Mime-type defaults
    mime_map = {
        "application/pdf": parse_pdf,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx,
        "application/vnd.ms-word": parse_docx,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": parse_pptx,
        "application/vnd.ms-powerpoint": parse_pptx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": parse_xlsx,
        "application/vnd.ms-excel": parse_xlsx,
        "text/csv": parse_csv,
        "text/plain": parse_txt,
        "text/markdown": parse_markdown,
        "application/json": parse_txt,
        "application/xml": parse_txt,
        "text/xml": parse_txt,
        "text/html": parse_txt,
    }

    if mime_type in mime_map:
        return mime_map[mime_type]

    if mime_type.startswith("text/"):
        return parse_txt
    if mime_type.startswith("image/"):
        return parse_image

    # Dynamic text detector wrapper
    def dynamic_parser_wrapper(file_bytes: bytes) -> Tuple[str, str, int, Dict[str, Any]]:
        try:
            if b"\x00" not in file_bytes[:8192]:
                title, content, pages, meta = parse_txt(file_bytes)
                return title, content, pages, {**meta, "inferred_type": "text"}
        except Exception:
            pass
        return parse_binary_fallback(file_bytes, filename or "unknown_asset", mime_type)

    return dynamic_parser_wrapper
