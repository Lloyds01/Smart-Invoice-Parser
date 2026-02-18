"""Pydantic request/response schemas shared by backend API endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ParseRequest(BaseModel):
    """Request schema for text parsing; accepts a single input or a batch."""

    content: str | None = Field(default=None, description="Single invoice-like text")
    contents: list[str] | None = Field(default=None, description="Multiple texts")

    @model_validator(mode="after")
    def validate_one_of(cls, values: "ParseRequest") -> "ParseRequest":
        """Ensure exactly one of `content` or `contents` is provided."""
        if (values.content is None and values.contents is None) or (
            values.content is not None and values.contents is not None
        ):
            raise ValueError("Provide either 'content' or 'contents'.")
        return values


class ParsedItem(BaseModel):
    """Structured output for one extracted product line."""

    product_name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    price: float | None = None
    price_type: Literal["total", "unit"] | None = None
    derived_unit_price: float | None = None
    raw_line: str
    confidence: float


class ParseResult(BaseModel):
    """Parsed items for one input blob identified by `input_index`."""

    input_index: int
    items: list[ParsedItem]


class ParseResponse(BaseModel):
    """Standard parse response containing deterministic request id and results."""

    request_id: str
    results: list[ParseResult]


class ParseImageResponse(ParseResponse):
    """Parse response extended with OCR text and source filename."""

    extracted_text: str
    filename: str


class ExportXlsxRequest(BaseModel):
    """Request schema for exporting parsed results to an Excel file."""

    results: list[ParseResult]


class HealthResponse(BaseModel):
    """Simple health-check response model."""

    status: str = "ok"
