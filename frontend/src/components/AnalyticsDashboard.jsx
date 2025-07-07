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
    dashboardType: 'custom',
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
      await deleteDashboardConfig(dashboardId)
      setDashboards(prev => prev.filter(d => d.id !== dashboardId))
      
      if (activeDashboard && activeDashboard.id === dashboardId) {
        setActiveDashboard(null)
      }
      
      setSuccess('Dashboard deleted successfully')
      setTimeout(() => setSuccess(null), 3000)
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
      dashboardType: 'custom',
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

  const DashboardConfigForm = () => (
    <div className="dashboard-form">
      <h3>Add New Dashboard</h3>
      
      <div className="form-group">
        <label>Dashboard Name:</label>
        <input
          type="text"
          name="dashboardName"
          value={dashboardForm.dashboardName}
          onChange={handleInputChange}
          placeholder="Enter dashboard name"
        />
      </div>
      
      <div className="form-group">
        <label>Dashboard Type:</label>
        <select 
          name="dashboardType" 
          value={dashboardForm.dashboardType}
          onChange={handleInputChange}
        >
          <option value="custom">Custom (iframe)</option>
          <option value="tableau">Tableau</option>
          <option value="powerbi">Power BI</option>
          <option value="grafana">Grafana</option>
          <option value="looker">Looker</option>
          <option value="metabase">Metabase</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Dashboard URL:</label>
        <input
          type="url"
          name="dashboardUrl"
          value={dashboardForm.dashboardUrl}
          onChange={handleInputChange}
          placeholder="https://your-dashboard-url.com"
        />
      </div>
      
      <div className="form-group">
        <label>Authentication Method:</label>
        <select 
          name="authenticationMethod" 
          value={dashboardForm.authenticationMethod}
          onChange={handleInputChange}
        >
          <option value="none">None</option>
          <option value="token">API Token</option>
          <option value="basic">Basic Auth</option>
          <option value="sso">SSO</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            name="isActive"
            checked={dashboardForm.isActive}
            onChange={handleInputChange}
          />
          Active
        </label>
      </div>
      
      <div className="form-actions">
        <button onClick={handleAddDashboard} disabled={loading || !dashboardForm.dashboardName || !dashboardForm.dashboardUrl}>
          Add Dashboard
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

    const handleIframeLoad = () => {
      setIframeLoading(false)
      setIframeError(false)
    }

    const handleIframeError = () => {
      setIframeLoading(false)
      setIframeError(true)
    }

    return (
      <div className="dashboard-viewer">
        <div className="viewer-header">
          <h3>{dashboard.dashboardName}</h3>
          <span className="dashboard-type">{dashboard.dashboardType}</span>
        </div>
        
        {iframeLoading && (
          <div className="iframe-loading">
            <p>Loading dashboard...</p>
          </div>
        )}
        
        {iframeError && (
          <div className="iframe-error">
            <p>Failed to load dashboard. Please check the URL and authentication settings.</p>
            <button onClick={() => window.open(dashboard.dashboardUrl, '_blank')}>
              Open in New Tab
            </button>
          </div>
        )}
        
        <iframe
          src={dashboard.dashboardUrl}
          width="100%"
          height="600"
          frameBorder="0"
          onLoad={handleIframeLoad}
          onError={handleIframeError}
          style={{ display: iframeError ? 'none' : 'block' }}
          sandbox="allow-scripts allow-same-origin allow-forms"
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
      <div className="dashboard-header">
        <h2>Analytics Dashboard</h2>
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
          <h3>No Dashboards Configured</h3>
          <p>Add your first dashboard to start viewing analytics and insights.</p>
          <button onClick={() => setShowAddForm(true)} className="btn-primary">
            Add Dashboard
          </button>
        </div>
      ) : (
        <>
          <div className="dashboard-tabs">
            {dashboards.map((dashboard) => (
              <button
                key={dashboard.id}
                className={`dashboard-tab ${activeDashboard?.id === dashboard.id ? 'active' : ''}`}
                onClick={() => setActiveDashboard(dashboard)}
              >
                {dashboard.dashboardName}
                <button
                  className="delete-tab"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteDashboard(dashboard.id)
                  }}
                  title="Delete dashboard"
                >
                  ×
                </button>
              </button>
            ))}
          </div>

          {activeDashboard && (
            <DashboardViewer dashboard={activeDashboard} />
          )}
        </>
      )}
    </div>
  )
}

export default AnalyticsDashboard