import React, { useState, useEffect } from 'react'
import api from '../services/api'

function StatusList() {
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchUploads()
    
    // Poll for updates every 30 seconds
    const interval = setInterval(fetchUploads, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const fetchUploads = async () => {
    try {
      console.log('📥 Fetching user uploads...')
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        console.log('❌ No token found')
        setLoading(false)
        return
      }

      const uploadsData = await api.getUserUploads()
      console.log('✅ Uploads fetched:', uploadsData)
      setUploads(uploadsData || [])
      setError(null)
    } catch (error) {
      console.error('❌ Error fetching uploads:', error)
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