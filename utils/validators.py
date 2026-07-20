"""Input sanitization and PDF/TXT document extraction validators."""

import io
import logging
import re

logger = logging.getLogger("MediAssistAI.Validators")


def sanitize_input(text: str) -> str:
    """Sanitize user text input to remove potential script injections or malicious characters."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]*>", "", text)
    # Remove control characters
    clean = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", clean)
    return clean.strip()


def extract_text_from_file(file_bytes: bytes, filename: str) -> tuple[bool, str]:
    """Extract plain text from uploaded PDF or TXT files.
    
    Returns:
        Tuple[bool, str]: (Success, Extracted Content or Error Message)
    """
    if not file_bytes:
        return False, "File is empty."

    filename_lower = filename.lower()

    if filename_lower.endswith(".txt"):
        try:
            content = file_bytes.decode("utf-8", errors="ignore")
            return True, sanitize_input(content)
        except Exception as e:
            return False, f"Failed to read TXT file: {e}"

    elif filename_lower.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_runs = []
            for page_idx, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text_runs.append(f"--- Page {page_idx + 1} ---\n{extracted}")

            full_text = "\n\n".join(text_runs)
            if not full_text.strip():
                return False, "PDF contains no extractable plain text (may be a scanned image)."
            return True, sanitize_input(full_text)
        except Exception as e:
            logger.error(f"Error parsing PDF with pypdf: {e}")
            return False, f"Failed to extract text from PDF document: {e}"

    return False, "Unsupported file format. Please upload a .pdf or .txt document."
