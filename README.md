# Smart Invoice Parser Monorepo

Production-style demo app for parsing unstructured invoice-like text with a regex-first extraction strategy.

## Structure
```text
backend/   FastAPI API + parser + tests
frontend/  React (Vite) UI
```

## Quick start

### 1) Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## API examples

### Health
```bash
curl http://localhost:8000/health
```

### Parse single
```bash
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"content":"Sugar – Rs. 6,000 (50 kg)\nWheat Flour (10kg @ 950)\nCooking Oil: Qty 5 bottles Price 1200/bottle"}'
```

### Parse batch
```bash
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"contents":["Sugar – Rs. 6,000 (50 kg)","Cooking Oil: Qty 5 bottles Price 1200/bottle"]}'
```

### Parse image
```bash
curl -X POST http://localhost:8000/parse-image \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/invoice.jpg"
```

### Export to Excel
```bash
curl -X POST http://localhost:8000/export/xlsx \
  -H "Content-Type: application/json" \
  -d '{"results":[{"input_index":0,"items":[{"product_name":"Sugar","quantity":50,"unit":"kg","price":6000,"price_type":"total","derived_unit_price":120,"raw_line":"Sugar – Rs. 6,000 (50 kg)","confidence":1}]}]}' \
  --output parsed_results.xlsx
```

## OCR prerequisite
Install Tesseract OCR so `/parse-image` can extract text from images.

macOS (Homebrew):
```bash
brew install tesseract
```

Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

## Assumptions
- Input is mostly line-oriented product descriptions.
- Regex-based parsing prioritizes precision over broad NLP recall.
- Noise lines (invoice ID, address, tax headings, totals) are ignored by heuristics.

## Limitations / trade-offs
- Regex patterns are deterministic but can miss uncommon formats.
- No OCR included; text must already be extracted.
- In-memory rate limiting is single-node only.

## Scaling notes
- 10k+ users/day:
  - Deploy backend behind a load balancer and API gateway.
  - Move rate limiting to Redis.
  - Add response caching for repeated identical payloads.
  - Use horizontal autoscaling for API pods/instances.
- Large documents:
  - Use streamed uploads and chunk parsing.
  - Split large content by sections/pages and aggregate results.
  - Offload long jobs to background workers.
- Async/background processing:
  - Queue parse tasks via Celery/RQ + Redis/RabbitMQ.
  - Store job status/results in DB.
  - Frontend polls or uses WebSocket/SSE for completion updates.

## Detailed guide
A detailed implementation/use-case guide is available at:
- `PROJECT_GUIDE.md`
