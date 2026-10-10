"""Document loader and text chunker for RAG pipeline.
Supports PDF, TXT, Markdown, and raw string inputs.
"""

import io
import re
from typing import List, Dict, Any, Optional

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from uploaded file bytes based on file extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if ext == 'pdf':
        if not PYPDF_AVAILABLE:
            raise RuntimeError("pypdf is required to read PDF files.")
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            if text.strip():
                pages_text.append(f"[Page {i+1}]\n{text}")
        return "\n\n".join(pages_text)
    
    # Text, Markdown, CSV, JSON, code files
    try:
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_bytes.decode('latin-1')
        except Exception as e:
            raise ValueError(f"Unable to decode text file '{filename}': {e}")


def clean_text(text: str) -> str:
    """Normalize whitespace, remove extraneous control characters."""
    if not text:
        return ""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def chunk_text(
    text: str,
    source_name: str = "Uploaded Document",
    chunk_size: int = 500,
    chunk_overlap: int = 80
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping semantic chunks with metadata.
    Attempts to split cleanly across sentences or paragraphs.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    # First split by paragraphs
    paragraphs = [p.strip() for p in cleaned.split('\n\n') if p.strip()]
    
    chunks: List[Dict[str, Any]] = []
    current_words: List[str] = []
    current_length = 0
    chunk_idx = 1

    # Approximate words
    for para in paragraphs:
        para_words = para.split()
        if not para_words:
            continue

        if current_length + len(para_words) <= chunk_size:
            current_words.extend(para_words)
            current_length += len(para_words)
        else:
            # If current_words is already substantial, save it
            if current_words:
                chunk_str = " ".join(current_words)
                chunks.append({
                    "id": f"{source_name}_chunk_{chunk_idx}",
                    "source": source_name,
                    "chunk_index": chunk_idx,
                    "text": chunk_str,
                    "word_count": len(current_words),
                    "char_count": len(chunk_str)
                })
                chunk_idx += 1
                # Overlap
                overlap_words = current_words[-chunk_overlap:] if chunk_overlap < len(current_words) else []
                current_words = overlap_words.copy()
                current_length = len(current_words)

            # Handle paragraph that exceeds chunk_size on its own
            while len(para_words) > chunk_size:
                take = para_words[:chunk_size]
                chunk_str = " ".join(take)
                chunks.append({
                    "id": f"{source_name}_chunk_{chunk_idx}",
                    "source": source_name,
                    "chunk_index": chunk_idx,
                    "text": chunk_str,
                    "word_count": len(take),
                    "char_count": len(chunk_str)
                })
                chunk_idx += 1
                para_words = para_words[chunk_size - chunk_overlap:]
            
            current_words.extend(para_words)
            current_length += len(para_words)

    if current_words:
        chunk_str = " ".join(current_words)
        chunks.append({
            "id": f"{source_name}_chunk_{chunk_idx}",
            "source": source_name,
            "chunk_index": chunk_idx,
            "text": chunk_str,
            "word_count": len(current_words),
            "char_count": len(chunk_str)
        })

    return chunks
