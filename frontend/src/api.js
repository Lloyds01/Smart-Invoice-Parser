const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function parseInvoice(content, signal) {
  const response = await fetch(`${API_BASE}/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
    signal,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    const message = data?.detail || `Request failed with ${response.status}`
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return response.json()
}

export async function parseInvoiceImage(file, signal) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/parse-image`, {
    method: 'POST',
    body: formData,
    signal,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    const message = data?.detail || `Request failed with ${response.status}`
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return response.json()
}

export async function exportResultsXlsx(results, signal) {
  const response = await fetch(`${API_BASE}/export/xlsx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ results }),
    signal,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    const message = data?.detail || `Request failed with ${response.status}`
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return response.blob()
}
