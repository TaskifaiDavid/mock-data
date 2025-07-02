import React from 'react'

function StatusItem({ upload }) {
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
    <div className="status-item">
      <div className="status-header">
        <h3>{upload.filename}</h3>
        <span className={`status-badge ${getStatusColor(upload.status)}`}>
          {upload.status}
        </span>
      </div>
      
      <div className="status-details">
        <p>
          <strong>Uploaded:</strong> {formatDate(upload.uploaded_at)}
        </p>
        
        {upload.status === 'completed' && (
          <>
            <p>
              <strong>Rows Processed:</strong> {upload.rows_processed || 0}
            </p>
            <p>
              <strong>Rows Cleaned:</strong> {upload.rows_cleaned || 0}
            </p>
            <p>
              <strong>Processing Time:</strong> {formatDuration(upload.processing_time_ms)}
            </p>
          </>
        )}
        
        {upload.status === 'failed' && upload.error_message && (
          <p className="error-message">
            <strong>Error:</strong> {upload.error_message}
          </p>
        )}
      </div>
    </div>
  )
}

export default StatusItem