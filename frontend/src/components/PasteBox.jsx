export default function PasteBox({
  value,
  onChange,
  onSubmit,
  onImageSelect,
  onImageSubmit,
  selectedImageName,
  loading,
}) {
  return (
    <section className="panel">
      <h2>Paste Invoice Text</h2>
      <textarea
        rows={10}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste invoice-like text here..."
      />
      <button onClick={onSubmit} disabled={loading || !value.trim()}>
        {loading ? 'Parsing...' : 'Parse'}
      </button>
      <div className="upload-row">
        <input
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/webp"
          onChange={(e) => onImageSelect(e.target.files?.[0] || null)}
        />
        <button onClick={onImageSubmit} disabled={loading || !selectedImageName}>
          Parse Uploaded Image
        </button>
      </div>
      {selectedImageName && <p className="muted">Selected image: {selectedImageName}</p>}
    </section>
  )
}
