# Frontend (React + Vite)

## Features
- Paste invoice text into textarea.
- Calls backend `/parse`.
- Uploads invoice image and calls `/parse-image`.
- Shows extracted rows in editable table.
- Supports partial fields (`null` values visible/editable).
- Error banner with retry, loading state, Copy JSON, and Download Excel action.

## Run locally
```bash
cd frontend
npm install
npm run dev
```

Optional backend URL override:
```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```
