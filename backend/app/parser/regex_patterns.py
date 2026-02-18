"""Regex definitions and noise filters used by the extraction engine."""

from __future__ import annotations
import re


# Order matters: more explicit patterns first.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "qty_price_slash_unit",
        re.compile(
            r"""
            ^\s*(?P<name>[A-Za-z][A-Za-z0-9\s\-\./&]+?)\s*[:\-]?\s*
            (?:qty|quantity)\s*(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z]+)?
            .*?
            (?:price\s*)?(?P<price>(?:rs\.?|pkr|\$)?\s*[\d,]+(?:\.\d+)?)\s*/\s*(?P<price_unit>[A-Za-z]+)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        "paren_qty_at_price",
        re.compile(
            r"""
            ^\s*(?P<name>[A-Za-z][A-Za-z0-9\s\-\./&]+?)\s*\(
            \s*(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z]+)\s*@\s*(?P<price>(?:rs\.?|pkr|\$)?\s*[\d,]+(?:\.\d+)?)
            \s*\)\s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        "dash_price_paren_qty",
        re.compile(
            r"""
            ^\s*(?P<name>[A-Za-z][A-Za-z0-9\s\-\./&]+?)\s*[\-–:]\s*
            (?P<price>(?:rs\.?|pkr|\$)?\s*[\d,]+(?:\.\d+)?)
            \s*\(\s*(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z]+)\s*\)\s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        "name_qty_unit_price",
        re.compile(
            r"""
            ^\s*(?P<name>[A-Za-z][A-Za-z0-9\s\-\./&]+?)\s+
            (?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z]+)
            .*?(?P<price>(?:rs\.?|pkr|\$)?\s*[\d,]+(?:\.\d+)?)\s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        "fallback_name_price",
        re.compile(
            r"""
            ^\s*(?P<name>[A-Za-z][A-Za-z0-9\s\-\./&]+?)\s*[\-–:]\s*
            (?P<price>(?:rs\.?|pkr|\$)?\s*[\d,]+(?:\.\d+)?)\s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
]


NOISE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\binvoice\s*(no|#|number)?\b", re.IGNORECASE),
    re.compile(r"\b(ntn|strn|tax|vat|gst)\b", re.IGNORECASE),
    re.compile(r"\btotal\s*(amount|due|tax)?\b", re.IGNORECASE),
    re.compile(r"\baddress\b", re.IGNORECASE),
    re.compile(r"^\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*$", re.IGNORECASE),
]
