"""Excel export service for converting parsed results into XLSX bytes."""

from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook

from app.schemas import ParseResult


HEADERS = [
    "input_index",
    "product_name",
    "quantity",
    "unit",
    "price",
    "price_type",
    "derived_unit_price",
    "raw_line",
    "confidence",
]


def build_xlsx_bytes(results: list[ParseResult]) -> bytes:
    """Create an XLSX workbook from parsed results and return it as bytes."""
    wb = Workbook()
    ws = wb.active
    ws.title = "parsed_items"

    ws.append(HEADERS)

    for group in results:
        for item in group.items:
            ws.append(
                [
                    group.input_index,
                    item.product_name,
                    item.quantity,
                    item.unit,
                    item.price,
                    item.price_type,
                    item.derived_unit_price,
                    item.raw_line,
                    item.confidence,
                ]
            )

    output = BytesIO()
    wb.save(output)
    return output.getvalue()
