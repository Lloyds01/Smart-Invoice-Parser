"""FastAPI application entrypoint and HTTP route handlers."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.middleware.payload_limit import PayloadLimitMiddleware
from app.middleware.rate_limit import FixedWindowRateLimitMiddleware
from app.parser import extract_items
from app.schemas import (
    ExportXlsxRequest,
    HealthResponse,
    ParseImageResponse,
    ParseRequest,
    ParseResponse,
    ParseResult,
    ParsedItem,
)
from app.services.excel import build_xlsx_bytes
from app.services.ocr import OCRInputError, OCRUnavailableError, extract_text_from_image_bytes

MAX_CHARS_PER_ITEM = 50_000
MULTIPART_AVAILABLE = importlib.util.find_spec("multipart") is not None

app = FastAPI(title="Smart Invoice Parser", version="1.0.0")

app.add_middleware(PayloadLimitMiddleware, max_bytes=200_000)
app.add_middleware(FixedWindowRateLimitMiddleware, requests_per_minute=120)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return a simple liveness response used by health checks."""
    return HealthResponse()


def stable_request_id(payload: dict) -> str:
    """Build a deterministic SHA256 hash for a JSON-serializable payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@app.post("/parse", response_model=ParseResponse)
def parse_invoice(request: ParseRequest) -> ParseResponse:
    """Parse one or many text inputs into structured invoice line items."""
    inputs = [request.content] if request.content is not None else request.contents or []

    for idx, text in enumerate(inputs):
        if len(text) > MAX_CHARS_PER_ITEM:
            raise HTTPException(
                status_code=413,
                detail=f"Input at index {idx} exceeds max character limit ({MAX_CHARS_PER_ITEM}).",
            )

    results: list[ParseResult] = []
    for i, text in enumerate(inputs):
        parsed = extract_items(text)
        results.append(
            ParseResult(
                input_index=i,
                items=[ParsedItem(**item.__dict__) for item in parsed],
            )
        )

    payload = {
        "content": request.content,
        "contents": request.contents,
        "results": [result.model_dump() for result in results],
    }
    request_id = stable_request_id(payload)
    return ParseResponse(request_id=request_id, results=results)


if MULTIPART_AVAILABLE:

    @app.post("/parse-image", response_model=ParseImageResponse)
    async def parse_invoice_image(file: UploadFile = File(...)) -> ParseImageResponse:
        """Run OCR on an uploaded image, then parse extracted text into line items."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing file name.")

        allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Allowed: PNG, JPG, JPEG, WEBP.",
            )

        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        try:
            text = extract_text_from_image_bytes(image_bytes)
        except OCRInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except OCRUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        parsed = extract_items(text)
        result = ParseResult(
            input_index=0,
            items=[ParsedItem(**item.__dict__) for item in parsed],
        )

        payload = {
            "filename": file.filename,
            "content_sha256": hashlib.sha256(image_bytes).hexdigest(),
            "results": [result.model_dump()],
        }
        request_id = stable_request_id(payload)
        return ParseImageResponse(
            request_id=request_id,
            extracted_text=text,
            filename=file.filename,
            results=[result],
        )

else:

    @app.post("/parse-image", response_model=ParseImageResponse)
    async def parse_invoice_image_unavailable() -> ParseImageResponse:
        """Return a clear error when image upload dependency is not installed."""
        raise HTTPException(
            status_code=503,
            detail="python-multipart is not installed. Install backend requirements to enable image upload.",
        )


@app.post("/export/xlsx")
def export_xlsx(request: ExportXlsxRequest) -> StreamingResponse:
    """Export parsed results to an in-memory Excel file and stream it to the client."""
    xlsx_bytes = build_xlsx_bytes(request.results)
    return StreamingResponse(
        BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=parsed_results.xlsx"},
    )
