# Backend (FastAPI)

## Features
- Regex-first parser for invoice-like unstructured text.
- Supports both single and batch input:
  - `{"content": "..."}`
  - `{"contents": ["...", "..."]}`
- Supports invoice image upload via OCR:
  - `POST /parse-image` (PNG/JPG/JPEG/WEBP)
- Supports Excel export:
  - `POST /export/xlsx`
- Partial extraction allowed (`null` fields are valid).
- Deterministic response with stable `request_id` hash.
- Middleware:
  - Payload size limit (`413`) via `PayloadLimitMiddleware`.
  - Fixed-window rate limiting (`429`) via `FixedWindowRateLimitMiddleware`.

## Run locally
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### OCR prerequisite
Image parsing requires Tesseract installed on your machine.

macOS (Homebrew):
```bash
brew install tesseract
```

Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

## Test
```bash
cd backend
source .venv/bin/activate
pytest -q
```

## Production notes
- Replace in-memory rate limit store with Redis for multi-instance deployments.
- Use trusted proxy settings before relying on `X-Forwarded-For` in production.
