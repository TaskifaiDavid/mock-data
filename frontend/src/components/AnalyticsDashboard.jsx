import React, { useState, useEffect } from 'react'
import { getDashboardConfigs, saveDashboardConfig, updateDashboardConfig, deleteDashboardConfig } from '../services/api'

const AnalyticsDashboard = () => {
  const [dashboards, setDashboards] = useState([])
  const [activeDashboard, setActiveDashboard] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  // Form state for adding/editing dashboards
  const [dashboardForm, setDashboardForm] = useState({
    dashboardName: '',
    dashboardType: 'looker',
    dashboardUrl: '',
    authenticationMethod: 'none',
    authenticationConfig: {},
    permissions: [],
    isActive: true
  })

  useEffect(() => {
    fetchDashboards()
  }, [])

  const fetchDashboards = async () => {
    try {
      setLoading(true)
      const response = await getDashboardConfigs()
      setDashboards(response.configs || [])
      
      // Set first active dashboard as default
      const activeConfig = response.configs?.find(d => d.isActive)
      if (activeConfig && !activeDashboard) {
        setActiveDashboard(activeConfig)
      }
    } catch (err) {
      console.error('Error fetching dashboards:', err)
      setError('Failed to load dashboard configurations')
    } finally {
      setLoading(false)
    }
  }

  const handleAddDashboard = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await saveDashboardConfig(dashboardForm)
      setDashboards(prev => [...prev, response.config])
      setShowAddForm(false)
      resetForm()
      setSuccess('Dashboard added successfully')
      
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error('Error adding dashboard:', err)
      setError('Failed to add dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDashboard = async (dashboardId) => {
    if (!confirm('Are you sure you want to delete this dashboard?')) return
    
    try {
      setLoading(true)
      const result = await deleteDashboardConfig(dashboardId)
      
      if (result && result.success) {
        setDashboards(prev => prev.filter(d => d.id !== dashboardId))
        
        if (activeDashboard && activeDashboard.id === dashboardId) {
          setActiveDashboard(null)
        }
        
        setSuccess('Dashboard deleted successfully')
        setTimeout(() => setSuccess(null), 3000)
      } else {
        throw new Error('Delete operation failed')
      }
    } catch (err) {
      console.error('Error deleting dashboard:', err)
      setError('Failed to delete dashboard')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setDashboardForm({
      dashboardName: '',
      dashboardType: 'looker',
      dashboardUrl: '',
      authenticationMethod: 'none',
      authenticationConfig: {},
      permissions: [],
      isActive: true
    })
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setDashboardForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }


  const handleOpenInLookerStudio = (dashboard) => {
    // Convert embed URL back to regular Looker Studio URL for manual refresh
    let originalUrl = dashboard.dashboardUrl
    if (originalUrl.includes('/embed/reporting/')) {
      originalUrl = originalUrl.replace('/embed/reporting/', '/reporting/')
    }
    // Remove any cache-busting parameters
    originalUrl = originalUrl.split('?')[0]
    window.open(originalUrl, '_blank')
  }

  const DashboardConfigForm = () => (
    <div className="dashboard-form">
      <h3>Add Google Looker Studio Dashboard</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-lg)', fontSize: '0.9rem' }}>
        Embed your Google Looker Studio dashboard by providing the shareable URL.
      </p>
      
      <div className="form-group">
        <label>Dashboard Name:</label>
        <input
          type="text"
          name="dashboardName"
          value={dashboardForm.dashboardName}
          onChange={handleInputChange}
          placeholder="Enter dashboard name (e.g., Sales Analytics)"
        />
      </div>
      
      <div className="form-group">
        <label>Google Looker Studio URL:</label>
        <input
          type="url"
          name="dashboardUrl"
          value={dashboardForm.dashboardUrl}
          onChange={handleInputChange}
          placeholder="https://lookerstudio.google.com/embed/reporting/..."
        />
        <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block' }}>
          Make sure to use the embed URL, not the regular viewing URL
        </small>
      </div>
      
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            name="isActive"
            checked={dashboardForm.isActive}
            onChange={handleInputChange}
          />
          Active Dashboard
        </label>
        <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block' }}>
          Only active dashboards will be displayed in the analytics section
        </small>
      </div>
      
      <div className="form-actions">
        <button onClick={handleAddDashboard} disabled={loading || !dashboardForm.dashboardName || !dashboardForm.dashboardUrl}>
          {loading ? 'Adding...' : 'Add Dashboard'}
        </button>
        <button onClick={() => setShowAddForm(false)} className="btn-secondary">
          Cancel
        </button>
      </div>
    </div>
  )

  const DashboardViewer = ({ dashboard }) => {
    const [iframeLoading, setIframeLoading] = useState(true)
    const [iframeError, setIframeError] = useState(false)
    const [lastRefreshed, setLastRefreshed] = useState(new Date())

    const handleIframeLoad = () => {
      setIframeLoading(false)
      setIframeError(false)
      setLastRefreshed(new Date())
    }

    const handleIframeError = () => {
      setIframeLoading(false)
      setIframeError(true)
    }

    // Helper function to ensure URL is properly formatted for embedding
    const getEmbedUrl = (url) => {
      if (!url) return url
      
      // If it's already an embed URL, return as is
      if (url.includes('/embed/')) {
        return url
      }
      
      // If it's a regular Looker Studio URL, try to convert to embed format
      if (url.includes('lookerstudio.google.com') && url.includes('/reporting/')) {
        return url.replace('/reporting/', '/embed/reporting/')
      }
      
      return url
    }

    const embedUrl = getEmbedUrl(dashboard.dashboardUrl)

    return (
      <div className="dashboard-viewer">
        <div className="viewer-header" style={{ marginBottom: '0.5rem', padding: '0.5rem 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.2rem' }}>{dashboard.dashboardName}</h3>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Google Looker Studio • Data refreshes automatically every 12 hours</span>
            </div>
          </div>
        </div>
        
        {iframeLoading && (
          <div className="iframe-loading">
            <p>Loading Google Looker Studio dashboard...</p>
            <small style={{ color: 'var(--text-muted)', marginTop: '0.5rem', display: 'block' }}>
              This may take a few moments
            </small>
          </div>
        )}
        
        {iframeError && (
          <div className="iframe-error">
            <p>Unable to load the dashboard. This could be due to:</p>
            <ul style={{ textAlign: 'left', margin: '1rem 0', paddingLeft: '1.5rem' }}>
              <li>The dashboard is not publicly shareable</li>
              <li>The URL is not an embed URL</li>
              <li>Your browser is blocking the content</li>
            </ul>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button onClick={() => window.open(embedUrl, '_blank')}>
                Open in New Tab
              </button>
              <button onClick={() => {
                setIframeError(false)
                setIframeLoading(true)
              }}>
                Retry
              </button>
            </div>
          </div>
        )}
        
        <iframe
          src={embedUrl}
          width="100%"
          height="900"
          frameBorder="0"
          onLoad={handleIframeLoad}
          onError={handleIframeError}
          className="dashboard-iframe"
          style={{ 
            display: iframeError ? 'none' : 'block',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            minHeight: '900px'
          }}
          allow="fullscreen"
          title={dashboard.dashboardName}
        />
      </div>
    )
  }

  if (loading && dashboards.length === 0) {
    return (
      <div className="analytics-dashboard">
        <div className="loading-state">
          <p>Loading dashboards...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header" style={{ padding: '1rem 0', marginBottom: '1rem' }}>
        <div className="header-left">
          <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.5rem' }}>Google Looker Studio</h2>
          {dashboards.length > 0 && (
            <select 
              value={activeDashboard?.id || ''} 
              onChange={(e) => {
                const selectedDashboard = dashboards.find(d => d.id === e.target.value)
                setActiveDashboard(selectedDashboard)
              }}
              className="dashboard-selector"
            >
              <option value="">Select a dashboard...</option>
              {dashboards.map((dashboard) => (
                <option key={dashboard.id} value={dashboard.id}>
                  {dashboard.dashboardName}
                </option>
              ))}
            </select>
          )}
        </div>
        <button 
          onClick={() => setShowAddForm(true)} 
          className="add-dashboard-btn"
          disabled={showAddForm}
        >
          + Add Dashboard
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      {showAddForm && <DashboardConfigForm />}

      {dashboards.length === 0 && !showAddForm ? (
        <div className="empty-state">
          <h3>No Google Looker Studio Dashboards</h3>
          <p>Connect your Google Looker Studio dashboards to view analytics and insights directly in TaskifAI.</p>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '1rem' }}>
            Note: Data in embedded dashboards refreshes automatically every 12 hours. For immediate data refresh, use the "Open in Looker Studio" button to manually refresh in the original dashboard.
          </p>
          <button onClick={() => setShowAddForm(true)} className="btn-primary">
            Add Google Looker Studio Dashboard
          </button>
        </div>
      ) : (
        <>
          {activeDashboard && (
            <div className="dashboard-management">
              <div className="dashboard-actions" style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <button
                  className="delete-dashboard-btn"
                  onClick={() => handleOpenInLookerStudio(activeDashboard)}
                  title="Open in Looker Studio to manually refresh data (Ctrl+Shift+E)"
                >
                  🔗 Open in Looker Studio
                </button>
                <button
                  className="delete-dashboard-btn"
                  onClick={() => handleDeleteDashboard(activeDashboard.id)}
                  title="Delete current dashboard"
                >
                  🗑️ Delete Dashboard
                </button>
              </div>
              <DashboardViewer dashboard={activeDashboard} />
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AnalyticsDashboard