# Project Guide (Detailed)

## Use case
This app extracts product-level data from noisy invoice-like text when invoices are pasted as unstructured text.
It is intended for workflows where strict document templates are unavailable.

## What the project does
- Splits input into candidate product lines.
- Ignores likely noise lines (invoice number, tax headers, address lines).
- Applies prioritized regex patterns.
- Returns optional fields when uncertain instead of forcing values.
- Computes confidence per item.
- Exposes parsing via FastAPI and a React UI with manual inline correction.

## Backend function map
- `backend/app/main.py`
  - `health()` -> liveness endpoint.
  - `stable_request_id()` -> deterministic hash for idempotent responses.
  - `parse_invoice()` -> accepts `content`/`contents`, validates max chars, parses, returns structured response.
  - `parse_invoice_image()` -> accepts uploaded image, runs OCR, parses extracted text.
  - `export_xlsx()` -> exports parsed/edited results to `.xlsx`.
- `backend/app/schemas.py`
  - Request and response Pydantic models.
- `backend/app/parser/regex_patterns.py`
  - Priority-ordered regex definitions.
  - Noise regex list.
- `backend/app/parser/postprocess.py`
  - Price cleaning, unit normalization, name normalization, confidence scoring.
- `backend/app/parser/extractor.py`
  - `split_candidate_lines()` -> line and delimiter-based splitting.
  - `is_noise_line()` -> line filtering.
  - `_extract_with_pattern()` -> pattern group to structured output.
  - `extract_from_line()` -> conflict resolution by confidence.
  - `extract_items()` -> end-to-end parse for one text blob.
- `backend/app/middleware/payload_limit.py`
  - Request payload byte limit and 413 responses.
- `backend/app/middleware/rate_limit.py`
  - In-memory per-IP fixed window limit and 429 responses.
- `backend/app/services/ocr.py`
  - OCR extraction from image bytes via Tesseract.
- `backend/app/services/excel.py`
  - Workbook generation for export.

## Developer notes (endpoint call paths)
- `GET /health`
  - `app.main.health()`
  - Returns `HealthResponse(status="ok")`
- `POST /parse`
  - `app.main.parse_invoice()`
  - Validates one-of input via `schemas.ParseRequest.validate_one_of()`
  - For each input: `parser.extractor.extract_items()`
  - Inside extractor:
    - `split_candidate_lines()` -> candidate line list
    - `extract_from_line()` per line
    - `extract_from_line()` applies regex list from `parser.regex_patterns.PATTERNS`
    - For each regex hit: `_extract_with_pattern()`
    - `_extract_with_pattern()` calls:
      - `postprocess.normalize_name()`
      - `postprocess.maybe_number()`
      - `postprocess.normalize_unit()`
      - `postprocess.clean_price()`
      - `postprocess.compute_confidence()`
  - Converts parser dataclasses to API schema objects: `schemas.ParsedItem`
  - Builds deterministic id with `app.main.stable_request_id()`
  - Returns `schemas.ParseResponse`
- `POST /parse-image`
  - `app.main.parse_invoice_image()` (or fallback `parse_invoice_image_unavailable()` when multipart is missing)
  - Validates MIME type and non-empty file
  - OCR call: `services.ocr.extract_text_from_image_bytes()`
  - OCR text then parsed by the same flow as `/parse` using `extract_items()`
  - Response id built by `stable_request_id()`
  - Returns `schemas.ParseImageResponse` (`results` + `extracted_text` + `filename`)
- `POST /export/xlsx`
  - `app.main.export_xlsx()`
  - Accepts `schemas.ExportXlsxRequest`
  - Excel bytes produced by `services.excel.build_xlsx_bytes()`
  - Returned as `StreamingResponse` with attachment filename `parsed_results.xlsx`

## Middleware order and behavior
- `PayloadLimitMiddleware` runs first for size protection (`413` on oversized body).
- `FixedWindowRateLimitMiddleware` enforces per-IP request budget (`429` when exceeded).
- CORS middleware allows local frontend origins (`http://localhost:5173`, `http://127.0.0.1:5173`).

## Frontend function map
- `frontend/src/api.js`
  - `parseInvoice()` -> HTTP client for `/parse`.
  - `parseInvoiceImage()` -> HTTP client for `/parse-image`.
  - `exportResultsXlsx()` -> HTTP client for `/export/xlsx`.
- `frontend/src/App.jsx`
  - Orchestrates text parse flow + image parse flow, loading/error states, editable result state, retry, copy JSON, and Excel download.
- `frontend/src/components/PasteBox.jsx`
  - Text input + parse action.
- `frontend/src/components/ResultsTable.jsx`
  - Grouped display by `input_index`.
- `frontend/src/components/EditableRow.jsx`
  - Inline row editing of nullable fields.

## Test coverage
- Required sample formats.
- Noise filtering.
- Multi-item split with semicolons.
- Derived unit price for total-price patterns.

## Operational notes
- Local-first architecture.
- Swap in-memory state (rate limit) with Redis for distributed deployments.
- For very large invoices, use chunking and background queues.
