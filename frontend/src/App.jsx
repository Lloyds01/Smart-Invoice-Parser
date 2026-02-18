import { useMemo, useRef, useState } from 'react'
import { exportResultsXlsx, parseInvoice, parseInvoiceImage } from './api'
import PasteBox from './components/PasteBox'
import ResultsTable from './components/ResultsTable'

const sample = `Invoice # INV-1001
Sugar – Rs. 6,000 (50 kg)
Wheat Flour (10kg @ 950)
Cooking Oil: Qty 5 bottles Price 1200/bottle`

export default function App() {
  const [content, setContent] = useState(sample)
  const [results, setResults] = useState([])
  const [selectedImage, setSelectedImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')
  const [ocrText, setOcrText] = useState('')
  const controllerRef = useRef(null)

  const canCopy = results.length > 0

  const copyPayload = useMemo(() => ({ results }), [results])

  async function runParse() {
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    setLoading(true)
    setError('')
    setOcrText('')

    try {
      const data = await parseInvoice(content, controller.signal)
      setResults(data.results || [])
    } catch (err) {
      setError(err.message || 'Failed to parse')
    } finally {
      setLoading(false)
    }
  }

  async function runImageParse() {
    if (!selectedImage) return

    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    setLoading(true)
    setError('')

    try {
      const data = await parseInvoiceImage(selectedImage, controller.signal)
      setResults(data.results || [])
      setOcrText(data.extracted_text || '')
    } catch (err) {
      setError(err.message || 'Failed to parse image')
    } finally {
      setLoading(false)
    }
  }

  function handleRowChange(groupIndex, rowIndex, field, value) {
    setResults((prev) => {
      const next = structuredClone(prev)
      if (!next[groupIndex]?.items[rowIndex]) return prev

      if (value === '') {
        next[groupIndex].items[rowIndex][field] = null
      } else if (['quantity', 'price', 'derived_unit_price', 'confidence'].includes(field)) {
        const parsed = Number(value)
        next[groupIndex].items[rowIndex][field] = Number.isFinite(parsed) ? parsed : value
      } else {
        next[groupIndex].items[rowIndex][field] = value
      }

      return next
    })
  }

  async function copyJson() {
    await navigator.clipboard.writeText(JSON.stringify(copyPayload, null, 2))
  }

  async function downloadExcel() {
    setDownloading(true)
    setError('')
    try {
      const blob = await exportResultsXlsx(results)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'parsed_results.xlsx'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err.message || 'Failed to export Excel')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <main className="container">
      <h1>Smart Invoice Parser</h1>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
          <button onClick={runParse}>Retry</button>
        </div>
      )}

      <PasteBox
        value={content}
        onChange={setContent}
        onSubmit={runParse}
        onImageSelect={setSelectedImage}
        onImageSubmit={runImageParse}
        selectedImageName={selectedImage?.name || ''}
        loading={loading}
      />

      {loading && <div className="loading">Parsing in progress...</div>}
      {!loading && ocrText && <div className="loading">OCR extracted text is included in results.</div>}

      <ResultsTable results={results} onRowChange={handleRowChange} />

      <button onClick={copyJson} disabled={!canCopy}>
        Copy JSON
      </button>
      <button onClick={downloadExcel} disabled={!canCopy || downloading}>
        {downloading ? 'Preparing Excel...' : 'Download Excel'}
      </button>
    </main>
  )
}
