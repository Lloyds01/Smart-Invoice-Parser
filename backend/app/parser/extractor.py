"""Core extraction pipeline that turns unstructured text into parsed invoice items."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.parser.postprocess import (
    clean_price,
    compute_confidence,
    maybe_number,
    normalize_name,
    normalize_unit,
)
from app.parser.regex_patterns import NOISE_PATTERNS, PATTERNS


@dataclass
class ParsedLine:
    """Internal parsed representation for one candidate invoice line."""

    product_name: str | None
    quantity: float | None
    unit: str | None
    price: float | None
    price_type: str | None
    derived_unit_price: float | None
    raw_line: str
    confidence: float


def split_candidate_lines(content: str) -> list[str]:
    """Split raw text into candidate lines, including basic multi-item line handling."""
    normalized = content.replace("\r", "\n")
    raw_lines = [line.strip() for line in normalized.split("\n") if line.strip()]

    result: list[str] = []
    for line in raw_lines:
        # If a line likely contains multiple items separated by commas/semicolons,
        # split only when each part still looks product-like.
        if ";" in line:
            parts = [p.strip() for p in line.split(";") if p.strip()]
            result.extend(parts)
            continue

        if ", " in line and sum(ch.isdigit() for ch in line) >= 2:
            parts = [p.strip() for p in line.split(", ") if p.strip()]
            product_like_parts = [p for p in parts if any(c.isalpha() for c in p)]
            if len(product_like_parts) > 1:
                result.extend(product_like_parts)
                continue

        result.append(line)

    return result


def is_noise_line(line: str) -> bool:
    """Return True when a line looks like metadata/noise instead of a product line."""
    lowered = line.lower().strip()
    if len(lowered) < 3:
        return True
    if all(not ch.isalpha() for ch in lowered):
        return True
    return any(pattern.search(lowered) for pattern in NOISE_PATTERNS)


def _extract_with_pattern(line: str, pattern_name: str, match: re.Match[str]) -> ParsedLine:
    """Map a regex match into normalized fields and compute confidence."""
    groups = match.groupdict()

    name = normalize_name(groups.get("name"))
    qty = maybe_number(groups.get("qty"))
    unit = normalize_unit(groups.get("unit") or groups.get("price_unit"))
    price = clean_price(groups.get("price"))

    price_type: str | None = None
    if pattern_name in {"paren_qty_at_price", "qty_price_slash_unit"}:
        price_type = "unit"
    elif pattern_name in {"dash_price_paren_qty", "fallback_name_price"}:
        price_type = "total"
    elif pattern_name == "name_qty_unit_price":
        price_type = "total" if qty and qty > 1 else "unit"

    derived_unit_price = None
    if price is not None and qty and qty > 0 and price_type == "total":
        derived_unit_price = round(price / qty, 4)

    fields = {
        "product_name": name,
        "quantity": qty,
        "unit": unit,
        "price": price,
        "price_type": price_type,
    }
    confidence = compute_confidence(fields, pattern_name)

    return ParsedLine(
        product_name=name,
        quantity=qty,
        unit=unit,
        price=price,
        price_type=price_type,
        derived_unit_price=derived_unit_price,
        raw_line=line,
        confidence=confidence,
    )


def extract_from_line(line: str) -> ParsedLine | None:
    """Parse one candidate line and resolve pattern conflicts by confidence score."""
    if is_noise_line(line):
        return None

    candidates: list[ParsedLine] = []

    for pattern_name, pattern in PATTERNS:
        match = pattern.match(line)
        if not match:
            continue
        candidates.append(_extract_with_pattern(line, pattern_name, match))

    if not candidates:
        return None

    # Conflict resolution: keep the highest-confidence candidate.
    # If tie, prefer the one with more populated fields then earlier pattern order.
    best = sorted(
        candidates,
        key=lambda c: (
            c.confidence,
            sum(
                value is not None and value != ""
                for value in [
                    c.product_name,
                    c.quantity,
                    c.unit,
                    c.price,
                    c.price_type,
                ]
            ),
        ),
        reverse=True,
    )[0]
    return best


def extract_items(content: str) -> list[ParsedLine]:
    """Run the full extraction pipeline on input text and return parsed product lines."""
    lines = split_candidate_lines(content)
    items: list[ParsedLine] = []
    for line in lines:
        parsed = extract_from_line(line)
        if parsed:
            items.append(parsed)
    return items
