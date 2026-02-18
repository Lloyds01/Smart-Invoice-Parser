import EditableRow from './EditableRow'

export default function ResultsTable({ results, onRowChange }) {
  if (!results?.length) return null

  return (
    <section className="panel">
      <h2>Parsed Results</h2>
      {results.map((group, groupIndex) => (
        <div key={groupIndex} className="group-block">
          <h3>Input #{group.input_index}</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Qty</th>
                  <th>Unit</th>
                  <th>Price</th>
                  <th>Price Type</th>
                  <th>Derived Unit Price</th>
                  <th>Confidence</th>
                  <th>Raw Line</th>
                </tr>
              </thead>
              <tbody>
                {group.items.map((row, rowIndex) => (
                  <EditableRow
                    key={rowIndex}
                    row={row}
                    onChange={(field, value) => onRowChange(groupIndex, rowIndex, field, value)}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </section>
  )
}
