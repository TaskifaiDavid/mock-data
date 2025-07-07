import React, { useState, useEffect } from 'react'
import StatusItem from './StatusItem'
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

  return (
    <div className="status-list">
      <h2>Processing Status</h2>
      
      {error && (
        <div className="error">Error loading uploads: {error}</div>
      )}
      
      {uploads.length === 0 ? (
        <p className="no-uploads">No uploads yet. Upload a file to get started!</p>
      ) : (
        <div className="uploads-grid">
          {uploads.map((upload) => (
            <StatusItem key={upload.id} upload={upload} />
          ))}
        </div>
      )}
    </div>
  )
}

export default StatusList