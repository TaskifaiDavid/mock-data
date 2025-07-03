import React, { useState, useRef } from 'react'
import api from '../services/api'

function Upload() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState([])
  const [error, setError] = useState(null)
  const [uploadMode, setUploadMode] = useState('single') // 'single' or 'multiple'
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files)
    
    if (uploadMode === 'single') {
      const selectedFile = selectedFiles[0]
      if (selectedFile && selectedFile.name.endsWith('.xlsx')) {
        setFiles([selectedFile])
        setError(null)
      } else {
        setError('Please select a valid .xlsx file')
        setFiles([])
      }
    } else {
      // Multiple mode - validate all files
      const validFiles = selectedFiles.filter(file => file.name.endsWith('.xlsx'))
      const invalidFiles = selectedFiles.filter(file => !file.name.endsWith('.xlsx'))
      
      if (invalidFiles.length > 0) {
        setError(`${invalidFiles.length} file(s) skipped - only .xlsx files are allowed`)
      } else {
        setError(null)
      }
      
      setFiles(validFiles)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    
    if (uploadMode === 'single') {
      const droppedFile = droppedFiles[0]
      if (droppedFile && droppedFile.name.endsWith('.xlsx')) {
        setFiles([droppedFile])
        setError(null)
      } else {
        setError('Please drop a valid .xlsx file')
        setFiles([])
      }
    } else {
      // Multiple mode
      const validFiles = droppedFiles.filter(file => file.name.endsWith('.xlsx'))
      const invalidFiles = droppedFiles.filter(file => !file.name.endsWith('.xlsx'))
      
      if (invalidFiles.length > 0) {
        setError(`${invalidFiles.length} file(s) skipped - only .xlsx files are allowed`)
      } else {
        setError(null)
      }
      
      setFiles(validFiles)
    }
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setError(null)
    setUploadResults([])

    try {
      let results
      if (uploadMode === 'single') {
        results = [await api.uploadFile(files[0])]
      } else {
        results = await api.uploadMultipleFiles(files)
      }
      
      setUploadResults(results)
      setFiles([])
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  return (
    <div className="upload-container">
      <h2>Upload Excel Files</h2>
      
      {/* Upload Mode Toggle */}
      <div className="upload-mode-toggle">
        <button 
          className={`btn-secondary ${uploadMode === 'single' ? 'active' : ''}`} 
          onClick={() => setUploadMode('single')}
        >
          Single File
        </button>
        <button 
          className={`btn-secondary ${uploadMode === 'multiple' ? 'active' : ''}`} 
          onClick={() => setUploadMode('multiple')}
        >
          Multiple Files
        </button>
      </div>
      
      <div
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx"
          multiple={uploadMode === 'multiple'}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="file-input"
        />
        
        <label htmlFor="file-input" className="upload-label">
          {files.length > 0 ? (
            <div className="files-selected">
              <p>{files.length} file(s) selected</p>
              {uploadMode === 'single' && (
                <p className="file-size">Size: {(files[0].size / 1024 / 1024).toFixed(2)} MB</p>
              )}
            </div>
          ) : (
            <>
              <p>Drag and drop your .xlsx file{uploadMode === 'multiple' ? 's' : ''} here</p>
              <p>or click to browse</p>
            </>
          )}
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="file-list">
          <h4>Selected Files:</h4>
          {files.map((file, index) => (
            <div key={index} className="file-item">
              <span className="file-name">{file.name}</span>
              <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
              {uploadMode === 'multiple' && (
                <button 
                  className="remove-file" 
                  onClick={() => removeFile(index)}
                  disabled={uploading}
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {files.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="upload-btn btn-primary"
        >
          {uploading ? 'Uploading...' : `Upload and Process ${files.length} File${files.length > 1 ? 's' : ''}`}
        </button>
      )}

      {uploadResults.length > 0 && (
        <div className="upload-results">
          <h3>Upload Results</h3>
          {uploadResults.map((result, index) => (
            <div key={index} className="upload-result">
              <p><strong>File:</strong> {result.filename}</p>
              <p><strong>Status:</strong> {result.status}</p>
              <p><strong>Upload ID:</strong> {result.id}</p>
            </div>
          ))}
          <p className="info">Your files are being processed in queue. Check the Processing Status tab for updates.</p>
        </div>
      )}
    </div>
  )
}

export default Upload