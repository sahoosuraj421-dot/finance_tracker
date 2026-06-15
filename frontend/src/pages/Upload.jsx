import { useState, useRef } from 'react'
import { Upload as UploadIcon, FileSpreadsheet, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '../services/api'

export default function Upload() {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return
    const ext = file.name.toLowerCase()
    if (!ext.endsWith('.csv') && !ext.endsWith('.xlsx') && !ext.endsWith('.xls')) {
      setError('Please upload a CSV or XLSX file.')
      return
    }

    setUploading(true)
    setError(null)
    setResult(null)

    try {
      const res = await api.uploadFile(file)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div className="page">
      <header className="page-header">
        <h2>Upload Data</h2>
        <p>Import transactions from CSV or Excel files</p>
      </header>

      <div
        className={`upload-zone ${dragging ? 'dragging' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          hidden
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <UploadIcon size={48} className="upload-icon" />
        <h3>Drop your file here or click to browse</h3>
        <p>Supports CSV, XLSX, and XLS files (max 10MB)</p>
        {uploading && <p className="upload-status">Uploading and parsing...</p>}
      </div>

      <div className="card info-card">
        <FileSpreadsheet size={20} />
        <div>
          <h4>Supported column names</h4>
          <p>Date: <code>date</code>, <code>transaction date</code> · Description: <code>description</code>, <code>memo</code>, <code>payee</code> · Amount: <code>amount</code>, <code>debit</code>/<code>credit</code> · Category: <code>category</code> (optional, auto-detected if missing)</p>
        </div>
      </div>

      {error && (
        <div className="result-banner error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="result-banner success">
          <CheckCircle size={20} />
          <div>
            <strong>{result.filename}</strong> imported successfully!
            <p>{result.rows_imported} transactions imported, {result.rows_skipped} rows skipped.</p>
            <p>Categories detected: {result.categories_detected.join(', ')}</p>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Sample CSV Format</h3>
        <pre className="code-block">{`date,description,amount,category
2025-01-15,Grocery Store,-85.50,Food & Dining
2025-01-16,Salary Deposit,3500.00,Salary & Income
2025-01-17,Netflix Subscription,-15.99,Entertainment
2025-01-18,Uber Ride,-24.00,Transportation`}</pre>
      </div>
    </div>
  )
}
