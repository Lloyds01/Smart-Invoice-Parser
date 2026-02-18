"""Post-processing helpers for normalization, numeric cleaning, and confidence scoring."""

from __future__ import annotations
import re
from typing import Any


UNIT_MAP = {
    "kg": "kg",
    "kgs": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "pc": "pcs",
    "pcs": "pcs",
    "piece": "pcs",
    "pieces": "pcs",
    "bottle": "bottles",
    "bottles": "bottles",
    "l": "l",
    "ltr": "l",
    "liter": "l",
    "liters": "l",
    "ml": "ml",
    "pack": "packs",
    "packs": "packs",
    "box": "boxes",
    "boxes": "boxes",
}


def clean_price(value: str | None) -> float | None:
    """Normalize currency/commas in a price string and return a float when valid."""
    if not value:
        return None
    cleaned = re.sub(r"(?i)(rs\.?|pkr|usd|\$)", "", value)
    cleaned = cleaned.replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_unit(value: str | None) -> str | None:
    """Map raw unit text to a canonical unit name (for example, `kgs` -> `kg`)."""
    if not value:
        return None
    lowered = value.strip().lower()
    return UNIT_MAP.get(lowered, lowered)


def normalize_name(name: str | None) -> str | None:
    """Trim punctuation/extra spaces and return a clean product name."""
    if not name:
        return None
    normalized = re.sub(r"\s+", " ", name).strip(" -:,.\t")
    return normalized if normalized else None


def maybe_number(value: str | None) -> float | None:
    """Convert a numeric string to float, returning None on invalid input."""
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def compute_confidence(fields: dict[str, Any], pattern_name: str) -> float:
    """Score extraction confidence from matched fields and pattern specificity."""
    score = 0.0

    if fields.get("product_name"):
        score += 0.35
    if fields.get("quantity") is not None:
        score += 0.2
    if fields.get("unit"):
        score += 0.1
    if fields.get("price") is not None:
        score += 0.25
    if fields.get("price_type"):
        score += 0.1

    if pattern_name in {"qty_price_slash_unit", "paren_qty_at_price", "dash_price_paren_qty"}:
        score += 0.05

    return max(0.0, min(1.0, round(score, 3)))
