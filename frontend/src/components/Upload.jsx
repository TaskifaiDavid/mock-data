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
      
      // Trigger status list refresh
      window.dispatchEvent(new Event('uploadComplete'))
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
    <div className="taskifai-upload-container">
      {/* Header Section */}
      <div className="upload-header">
        <div className="header-content">
          <div className="header-icon">📊</div>
          <div className="header-text">
            <h2>Transform Your Data</h2>
            <p>Upload Excel files and get instant AI-powered insights</p>
          </div>
        </div>
      </div>
      
      {/* Upload Mode Toggle */}
      <div className="taskifai-mode-toggle">
        <div className="mode-label">
          <span>Upload Mode</span>
        </div>
        <div className="toggle-buttons">
          <button 
            className={`mode-btn ${uploadMode === 'single' ? 'active' : ''}`} 
            onClick={() => setUploadMode('single')}
          >
            <span className="mode-icon">📄</span>
            <span className="mode-text">Single File</span>
          </button>
          <button 
            className={`mode-btn ${uploadMode === 'multiple' ? 'active' : ''}`} 
            onClick={() => setUploadMode('multiple')}
          >
            <span className="mode-icon">📋</span>
            <span className="mode-text">Multiple Files</span>
          </button>
        </div>
      </div>
      
      {/* Upload Area */}
      <div
        className="taskifai-upload-area"
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
        
        <label htmlFor="file-input" className="upload-zone">
          {files.length > 0 ? (
            <div className="files-selected">
              <div className="selection-icon">✅</div>
              <div className="selection-text">
                <h3>{files.length} file{files.length > 1 ? 's' : ''} ready to upload</h3>
                {uploadMode === 'single' && (
                  <p>Size: {(files[0].size / 1024 / 1024).toFixed(2)} MB</p>
                )}
              </div>
            </div>
          ) : (
            <div className="upload-prompt">
              <div className="upload-icon">☁️</div>
              <div className="upload-text">
                <h3>Drag & drop your Excel file{uploadMode === 'multiple' ? 's' : ''}</h3>
                <p>or <span className="browse-text">click to browse</span></p>
                <div className="file-info">
                  <span className="file-type">Supports .xlsx files only</span>
                </div>
              </div>
            </div>
          )}
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="taskifai-file-list">
          <div className="list-header">
            <h4>Selected Files</h4>
            <span className="file-count">{files.length} file{files.length > 1 ? 's' : ''}</span>
          </div>
          <div className="file-items">
            {files.map((file, index) => (
              <div key={index} className="taskifai-file-item">
                <div className="file-icon">📊</div>
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-meta">
                    <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    <span className="file-type">Excel Spreadsheet</span>
                  </div>
                </div>
                {uploadMode === 'multiple' && (
                  <button 
                    className="remove-btn" 
                    onClick={() => removeFile(index)}
                    disabled={uploading}
                    title="Remove file"
                  >
                    <span>×</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="taskifai-error">
          <div className="error-icon">⚠️</div>
          <div className="error-text">{error}</div>
        </div>
      )}

      {/* Upload Button */}
      {files.length > 0 && (
        <div className="upload-actions">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="taskifai-upload-btn"
          >
            {uploading ? (
              <>
                <span className="loading-spinner"></span>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span className="upload-btn-icon">🚀</span>
                <span>Transform {files.length} File{files.length > 1 ? 's' : ''}</span>
              </>
            )}
          </button>
          <div className="upload-info">
            <span>Your data will be processed securely with AI-powered insights</span>
          </div>
        </div>
      )}

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="taskifai-results">
          <div className="results-header">
            <div className="results-icon">✨</div>
            <div className="results-text">
              <h3>Upload Successful!</h3>
              <p>Your files are being transformed into insights</p>
            </div>
          </div>
          <div className="results-list">
            {uploadResults.map((result, index) => (
              <div key={index} className="result-item">
                <div className="result-status">
                  <div className="status-icon">✅</div>
                  <div className="status-text">
                    <div className="file-name">{result.filename}</div>
                    <div className="upload-id">ID: {result.id}</div>
                  </div>
                </div>
                <div className="status-badge">{result.status}</div>
              </div>
            ))}
          </div>
          <div className="results-footer">
            <div className="info-icon">💡</div>
            <span>Check the Status tab to monitor processing progress and view insights when ready.</span>
          </div>
        </div>
      )}

      <style jsx>{`
        .taskifai-upload-container {
          max-width: 800px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .upload-header {
          text-align: center;
          margin-bottom: 1rem;
        }

        .header-content {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .header-icon {
          font-size: 3rem;
          opacity: 0.9;
        }

        .header-text h2 {
          font-size: 1.7rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 0.5rem 0;
        }

        .header-text p {
          font-size: 0.96rem;
          color: var(--text-secondary);
          margin: 0;
          opacity: 0.8;
        }

        .taskifai-mode-toggle {
          background: var(--surface-primary);
          padding: var(--spacing-lg);
          border-radius: var(--radius-xl);
          border: 1px solid var(--border-light);
          box-shadow: var(--shadow-sm);
        }

        .mode-label {
          margin-bottom: 1rem;
        }

        .mode-label span {
          font-size: 0.95rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        .toggle-buttons {
          display: flex;
          gap: 0.5rem;
        }

        .mode-btn {
          flex: 1;
          padding: 1rem;
          background: var(--surface-primary);
          border: 2px solid var(--border-light);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          font-size: 0.95rem;
          font-weight: 500;
          color: var(--text-secondary);
        }

        .mode-btn:hover:not(.active) {
          background: var(--surface-secondary);
          border-color: var(--border-medium);
          color: var(--text-primary);
          transform: translateY(-2px);
        }

        .mode-btn.active {
          background: var(--notion-black);
          border-color: transparent;
          color: var(--notion-white);
          box-shadow: var(--shadow-md);
        }

        .mode-icon {
          font-size: 1.25rem;
        }

        .taskifai-upload-area {
          background: var(--surface-primary);
          border-radius: 20px;
          border: 2px dashed var(--border-light);
          transition: all 0.3s ease;
          box-shadow: var(--shadow-sm);
        }

        .taskifai-upload-area:hover {
          border-color: var(--border-medium);
          box-shadow: var(--shadow-md);
        }

        .upload-zone {
          display: block;
          padding: 3rem 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .upload-zone:hover {
          transform: translateY(-4px);
        }

        .files-selected {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
        }

        .selection-icon {
          font-size: 3rem;
          opacity: 0.8;
        }

        .selection-text h3 {
          font-size: 1.275rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 0.25rem 0;
        }

        .selection-text p {
          font-size: 1rem;
          color: var(--text-muted);
          margin: 0;
        }

        .upload-prompt {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .upload-icon {
          font-size: 4rem;
          opacity: 0.7;
        }

        .upload-text h3 {
          font-size: 1.275rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 0.5rem 0;
        }

        .upload-text p {
          font-size: 0.96rem;
          color: var(--text-secondary);
          margin: 0;
        }

        .browse-text {
          color: var(--text-primary);
          font-weight: 600;
          text-decoration: underline;
        }

        .file-info {
          margin-top: 1rem;
        }

        .file-type {
          background: var(--surface-secondary);
          color: var(--text-primary);
          padding: var(--spacing-xs) var(--spacing-md);
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
          border: 1px solid var(--border-light);
        }

        .taskifai-file-list {
          background: var(--surface-primary);
          padding: var(--spacing-lg);
          border-radius: var(--radius-xl);
          border: 1px solid var(--border-light);
          box-shadow: var(--shadow-sm);
        }

        .list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid var(--border-light);
        }

        .list-header h4 {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .file-count {
          background: var(--surface-secondary);
          color: var(--text-primary);
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-lg);
          font-size: 0.75rem;
          font-weight: 600;
          border: 1px solid var(--border-light);
        }

        .file-items {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .taskifai-file-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background: var(--surface-primary);
          border-radius: 12px;
          border: 1px solid var(--border-light);
          transition: all 0.2s ease;
        }

        .taskifai-file-item:hover {
          background: var(--surface-secondary);
          border-color: var(--border-medium);
        }

        .file-icon {
          font-size: 2rem;
          opacity: 0.8;
        }

        .file-info {
          flex: 1;
        }

        .file-name {
          font-size: 1rem;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .file-meta {
          display: flex;
          gap: 1rem;
        }

        .file-size, .file-type {
          font-size: 0.875rem;
          color: var(--text-muted);
        }

        .remove-btn {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background-color: var(--neutral-200);
          color: var(--text-secondary);
          border: none;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.25rem;
          line-height: 1;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .remove-btn:hover:not(:disabled) {
          background-color: #FEE2E2;
          color: #DC2626;
          transform: scale(1.1);
        }

        .taskifai-error {
          display: flex;
          align-items: center;
          gap: 1rem;
          background: #FEF2F2;
          border: 1px solid #FECACA;
          color: #DC2626;
          padding: 1rem 1.5rem;
          border-radius: 12px;
          font-size: 0.95rem;
        }

        .error-icon {
          font-size: 1.5rem;
        }

        .upload-actions {
          text-align: center;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .taskifai-upload-btn {
          width: 100%;
          padding: var(--spacing-md) var(--spacing-xl);
          background: var(--notion-black);
          color: var(--notion-white);
          border: none;
          border-radius: var(--radius-xl);
          font-size: 0.96rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
          box-shadow: var(--shadow-md);
        }

        .taskifai-upload-btn:hover:not(:disabled) {
          background: var(--neutral-800);
          transform: translateY(-2px);
          box-shadow: var(--shadow-lg);
        }

        .taskifai-upload-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }

        .upload-btn-icon {
          font-size: 1.25rem;
        }

        .loading-spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .upload-info {
          font-size: 0.95rem;
          color: var(--text-muted);
          opacity: 0.8;
        }

        .taskifai-results {
          background: var(--surface-primary);
          padding: var(--spacing-xl);
          border-radius: 20px;
          border: 1px solid var(--border-light);
          box-shadow: var(--shadow-sm);
        }

        .results-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
          text-align: center;
          justify-content: center;
        }

        .results-icon {
          font-size: 3rem;
        }

        .results-text h3 {
          font-size: 1.275rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 0.25rem 0;
        }

        .results-text p {
          font-size: 1rem;
          color: var(--text-secondary);
          margin: 0;
          opacity: 0.8;
        }

        .results-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .result-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: var(--surface-primary);
          border-radius: 12px;
          border: 1px solid var(--border-light);
        }

        .result-status {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .status-icon {
          font-size: 1.5rem;
        }

        .status-text .file-name {
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .upload-id {
          font-size: 0.875rem;
          color: var(--text-muted);
          font-family: monospace;
        }

        .status-badge {
          background: #D1FAE5;
          color: #065F46;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.875rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .results-footer {
          display: flex;
          align-items: flex-start;
          gap: var(--spacing-sm);
          background: var(--surface-secondary);
          padding: var(--spacing-md);
          border-radius: var(--radius-lg);
          font-size: 0.8rem;
          color: var(--text-secondary);
          line-height: 1.5;
          border: 1px solid var(--border-light);
        }

        .info-icon {
          font-size: 1.25rem;
          margin-top: 0.125rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .taskifai-upload-container {
            gap: 1.5rem;
          }

          .header-content {
            flex-direction: column;
            gap: 0.75rem;
          }

          .header-icon {
            font-size: 2.5rem;
          }

          .header-text h2 {
            font-size: 1.75rem;
          }

          .header-text p {
            font-size: 1rem;
          }

          .toggle-buttons {
            flex-direction: column;
            gap: 0.75rem;
          }

          .mode-btn {
            justify-content: flex-start;
            padding: 1rem 1.25rem;
          }

          .upload-zone {
            padding: 2rem 1rem;
          }

          .upload-icon {
            font-size: 3rem;
          }

          .upload-text h3 {
            font-size: 1.25rem;
          }

          .upload-text p {
            font-size: 1rem;
          }

          .files-selected {
            flex-direction: column;
            gap: 0.75rem;
          }

          .selection-icon {
            font-size: 2.5rem;
          }

          .taskifai-file-item {
            padding: 0.75rem;
          }

          .file-meta {
            flex-direction: column;
            gap: 0.25rem;
          }

          .results-header {
            flex-direction: column;
            gap: 0.75rem;
          }

          .results-icon {
            font-size: 2.5rem;
          }
        }

        @media (max-width: 480px) {
          .taskifai-upload-container {
            gap: 1rem;
          }

          .taskifai-mode-toggle,
          .taskifai-file-list,
          .taskifai-results {
            padding: 1rem;
          }

          .upload-zone {
            padding: 1.5rem 0.75rem;
          }

          .taskifai-upload-btn {
            padding: 1rem 1.5rem;
            font-size: 1rem;
          }

          .result-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
          }

          .status-badge {
            align-self: flex-end;
          }
        }
      `}</style>
    </div>
  )
}

export default Upload