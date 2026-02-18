"""OCR service helpers for extracting text from uploaded invoice images."""

from __future__ import annotations

import io

from PIL import Image, UnidentifiedImageError


class OCRUnavailableError(RuntimeError):
    """Raised when OCR dependencies or engine are unavailable."""

    pass


class OCRInputError(ValueError):
    """Raised when uploaded image bytes cannot be decoded as a valid image."""

    pass


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """Extract text from image bytes using Tesseract OCR."""
    try:
        import pytesseract
        from pytesseract import TesseractNotFoundError
    except ModuleNotFoundError as exc:
        raise OCRUnavailableError(
            "pytesseract is not installed. Install backend requirements to enable image parsing."
        ) from exc

    try:
        image = Image.open(io.BytesIO(image_bytes))
    except UnidentifiedImageError as exc:
        raise OCRInputError("Unsupported or invalid image file.") from exc

    try:
        text = pytesseract.image_to_string(image)
    except TesseractNotFoundError as exc:
        raise OCRUnavailableError(
            "Tesseract OCR engine is not installed or not in PATH. "
            "Install it to enable image parsing."
        ) from exc

    return text.strip()
