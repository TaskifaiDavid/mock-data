import React, { useState, useEffect } from 'react'
import api from '../services/api'

function StatusList() {
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchUploads()
    
    // Poll for updates every 10 seconds for better real-time updates
    const interval = setInterval(fetchUploads, 10000)
    
    return () => clearInterval(interval)
  }, [])

  // Add refresh function that can be called externally
  useEffect(() => {
    // Listen for upload completion events
    const handleUploadComplete = () => {
      fetchUploads()
    }

    window.addEventListener('uploadComplete', handleUploadComplete)
    
    return () => {
      window.removeEventListener('uploadComplete', handleUploadComplete)
    }
  }, [])

  const fetchUploads = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        setLoading(false)
        return
      }

      const uploadsData = await api.getUserUploads()
      setUploads(uploadsData || [])
      setError(null)
    } catch (error) {
      // Keep essential error logging for production debugging
      console.error('Failed to fetch uploads:', error.message)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading processing status...</div>
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'status-success'
      case 'failed':
        return 'status-error'
      case 'processing':
        return 'status-processing'
      default:
        return 'status-pending'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const formatDuration = (ms) => {
    if (!ms) return 'N/A'
    return `${(ms / 1000).toFixed(2)}s`
  }

  return (
    <div className="status-list">
      <h2>Processing Status</h2>
      
      {error && (
        <div className="error">Error loading uploads: {error}</div>
      )}
      
      {uploads.length === 0 ? (
        <p className="no-uploads">No uploads yet. Upload a file to get started!</p>
      ) : (
        <div className="status-table-container">
          <table className="status-table">
            <thead>
              <tr>
                <th>File Name</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Rows Processed</th>
                <th>Rows Cleaned</th>
                <th>Processing Time</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {uploads.map((upload) => (
                <tr key={upload.id}>
                  <td className="filename">{upload.filename}</td>
                  <td>
                    <span className={`status-badge ${getStatusColor(upload.status)}`}>
                      {upload.status}
                    </span>
                  </td>
                  <td>{formatDate(upload.uploaded_at)}</td>
                  <td>{upload.rows_processed || '-'}</td>
                  <td>{upload.rows_cleaned || '-'}</td>
                  <td>{formatDuration(upload.processing_time_ms)}</td>
                  <td className="error-cell">
                    {upload.status === 'failed' && upload.error_message ? (
                      <span className="error-message" title={upload.error_message}>
                        {upload.error_message.length > 50 
                          ? `${upload.error_message.substring(0, 50)}...` 
                          : upload.error_message}
                      </span>
                    ) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default StatusList