import React, { useState, useEffect } from 'react'
import api from '../services/api'

function StatusList() {
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState({
    status: [],
    rows_processed: [],
    rows_cleaned: []
  })
  const [openDropdown, setOpenDropdown] = useState(null)

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

  // Get unique values for each filterable column
  const getUniqueValues = (key) => {
    const values = uploads.map(upload => {
      if (key === 'rows_processed' || key === 'rows_cleaned') {
        return upload[key] || '-'
      }
      return upload[key]
    })
    return [...new Set(values)].sort()
  }

  // Handle filter toggle
  const toggleFilter = (column, value) => {
    setFilters(prev => {
      const currentFilters = prev[column]
      const newFilters = currentFilters.includes(value)
        ? currentFilters.filter(v => v !== value)
        : [...currentFilters, value]
      return { ...prev, [column]: newFilters }
    })
  }

  // Clear all filters
  const clearAllFilters = () => {
    setFilters({
      status: [],
      rows_processed: [],
      rows_cleaned: []
    })
    setSearchTerm('')
  }

  // Apply filters
  const filteredUploads = uploads.filter(upload => {
    // Search filter
    if (searchTerm && !upload.filename.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }

    // Status filter
    if (filters.status.length > 0 && !filters.status.includes(upload.status)) {
      return false
    }

    // Rows processed filter
    if (filters.rows_processed.length > 0) {
      const value = upload.rows_processed || '-'
      if (!filters.rows_processed.includes(value)) {
        return false
      }
    }

    // Rows cleaned filter
    if (filters.rows_cleaned.length > 0) {
      const value = upload.rows_cleaned || '-'
      if (!filters.rows_cleaned.includes(value)) {
        return false
      }
    }

    return true
  })

  // Check if any filters are active
  const hasActiveFilters = searchTerm ||
    filters.status.length > 0 ||
    filters.rows_processed.length > 0 ||
    filters.rows_cleaned.length > 0

  return (
    <div className="status-list">
      <h2>Processing Status</h2>

      {error && (
        <div className="error">Error loading uploads: {error}</div>
      )}

      {uploads.length === 0 ? (
        <p className="no-uploads">No uploads yet. Upload a file to get started!</p>
      ) : (
        <>
          <div className="filter-controls">
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search by filename..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="clear-search"
                  title="Clear search"
                >
                  ×
                </button>
              )}
            </div>
            {hasActiveFilters && (
              <button onClick={clearAllFilters} className="clear-all-filters">
                Clear All Filters
              </button>
            )}
          </div>

          {filteredUploads.length === 0 ? (
            <p className="no-uploads">No files found matching "{searchTerm}"</p>
          ) : (
            <div className="status-table-container">
          <table className="status-table">
            <thead>
              <tr>
                <th>File Name</th>
                <th className="filterable-column">
                  <div className="column-header">
                    <span>Status</span>
                    <button
                      className={`filter-icon ${filters.status.length > 0 ? 'active' : ''}`}
                      onClick={() => setOpenDropdown(openDropdown === 'status' ? null : 'status')}
                      title="Filter status"
                    >
                      ⋮
                    </button>
                    {openDropdown === 'status' && (
                      <div className="filter-dropdown">
                        <div className="filter-options">
                          {getUniqueValues('status').map(value => (
                            <label key={value} className="filter-option">
                              <input
                                type="checkbox"
                                checked={filters.status.includes(value)}
                                onChange={() => toggleFilter('status', value)}
                              />
                              <span>{value}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </th>
                <th>Uploaded</th>
                <th className="filterable-column">
                  <div className="column-header">
                    <span>Rows Processed</span>
                    <button
                      className={`filter-icon ${filters.rows_processed.length > 0 ? 'active' : ''}`}
                      onClick={() => setOpenDropdown(openDropdown === 'rows_processed' ? null : 'rows_processed')}
                      title="Filter rows processed"
                    >
                      ⋮
                    </button>
                    {openDropdown === 'rows_processed' && (
                      <div className="filter-dropdown">
                        <div className="filter-options">
                          {getUniqueValues('rows_processed').map(value => (
                            <label key={value} className="filter-option">
                              <input
                                type="checkbox"
                                checked={filters.rows_processed.includes(value)}
                                onChange={() => toggleFilter('rows_processed', value)}
                              />
                              <span>{value}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </th>
                <th className="filterable-column">
                  <div className="column-header">
                    <span>Rows Cleaned</span>
                    <button
                      className={`filter-icon ${filters.rows_cleaned.length > 0 ? 'active' : ''}`}
                      onClick={() => setOpenDropdown(openDropdown === 'rows_cleaned' ? null : 'rows_cleaned')}
                      title="Filter rows cleaned"
                    >
                      ⋮
                    </button>
                    {openDropdown === 'rows_cleaned' && (
                      <div className="filter-dropdown">
                        <div className="filter-options">
                          {getUniqueValues('rows_cleaned').map(value => (
                            <label key={value} className="filter-option">
                              <input
                                type="checkbox"
                                checked={filters.rows_cleaned.includes(value)}
                                onChange={() => toggleFilter('rows_cleaned', value)}
                              />
                              <span>{value}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </th>
                <th>Processing Time</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {filteredUploads.map((upload) => (
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
        </>
      )}
    </div>
  )
}

export default StatusList