import React, { useState, useRef } from 'react'
import api from '../services/api'

function Upload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.name.endsWith('.xlsx')) {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Please select a valid .xlsx file')
      setFile(null)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.xlsx')) {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Please drop a valid .xlsx file')
      setFile(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setUploadResult(null)

    try {
      const result = await api.uploadFile(file)
      setUploadResult(result)
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-container">
      <h2>Upload Excel File</h2>
      
      <div
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="file-input"
        />
        
        <label htmlFor="file-input" className="upload-label">
          {file ? (
            <div className="file-selected">
              <p>Selected file: {file.name}</p>
              <p className="file-size">Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <>
              <p>Drag and drop your .xlsx file here</p>
              <p>or click to browse</p>
            </>
          )}
        </label>
      </div>

      {error && <div className="error">{error}</div>}

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="upload-btn"
        >
          {uploading ? 'Uploading...' : 'Upload and Process'}
        </button>
      )}

      {uploadResult && (
        <div className="upload-result">
          <h3>Upload Successful!</h3>
          <p>File: {uploadResult.filename}</p>
          <p>Upload ID: {uploadResult.id}</p>
          <p>Status: {uploadResult.status}</p>
          <p className="info">Your file is being processed. Check the Processing Status tab for updates.</p>
        </div>
      )}
    </div>
  )
}

export default Upload