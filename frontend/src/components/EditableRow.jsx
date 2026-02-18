const fields = [
  'product_name',
  'quantity',
  'unit',
  'price',
  'price_type',
  'derived_unit_price',
  'confidence',
]

export default function EditableRow({ row, onChange }) {
  return (
    <tr>
      {fields.map((field) => (
        <td key={field}>
          <input
            value={row[field] ?? ''}
            onChange={(e) => onChange(field, e.target.value)}
            placeholder="null"
          />
        </td>
      ))}
      <td title={row.raw_line}>{row.raw_line}</td>
    </tr>
  )
}
