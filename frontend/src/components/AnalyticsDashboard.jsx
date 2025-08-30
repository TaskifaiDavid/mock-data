import React, { useState, useEffect, useRef, useCallback } from 'react'
import { getDashboardConfigs, saveDashboardConfig, updateDashboardConfig, deleteDashboardConfig } from '../services/api'

// Toast notification component
const Toast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className={`toast toast-${type}`}>
      <div className="toast-content">
        <span className={`toast-icon ${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ⓘ'}`}>
          {type === 'success' ? '✓' : type === 'error' ? '✗' : 'ⓘ'}
        </span>
        <span className="toast-message">{message}</span>
        <button className="toast-close" onClick={onClose}>×</button>
      </div>
    </div>
  )
}

// URL validation functions
const validateDashboardUrl = (url, type) => {
  if (!url) return { isValid: false, message: 'URL is required' }
  
  try {
    new URL(url)
  } catch {
    return { isValid: false, message: 'Please enter a valid URL' }
  }
  
  const urlLower = url.toLowerCase()
  
  switch (type) {
    case 'looker':
      if (!urlLower.includes('lookerstudio.google.com')) {
        return { isValid: false, message: 'Please enter a valid Google Looker Studio URL' }
      }
      if (!urlLower.includes('/reporting/') && !urlLower.includes('/embed/reporting/')) {
        return { isValid: false, message: 'URL must contain /reporting/ or /embed/reporting/' }
      }
      return { isValid: true, message: 'Valid Google Looker Studio URL' }
    
    case 'google_analytics':
      if (!urlLower.includes('analytics.google.com')) {
        return { isValid: false, message: 'Please enter a valid Google Analytics URL' }
      }
      return { isValid: true, message: 'Valid Google Analytics URL' }
    
    case 'tableau':
      if (!urlLower.includes('tableau') && !urlLower.includes('public.tableau.com')) {
        return { isValid: false, message: 'Please enter a valid Tableau URL' }
      }
      return { isValid: true, message: 'Valid Tableau URL' }
    
    case 'power_bi':
      if (!urlLower.includes('powerbi.microsoft.com') && !urlLower.includes('app.powerbi.com')) {
        return { isValid: false, message: 'Please enter a valid Power BI URL' }
      }
      return { isValid: true, message: 'Valid Power BI URL' }
    
    default:
      return { isValid: true, message: 'URL format appears valid' }
  }
}

// Enhanced Dashboard Form Component
const DashboardConfigForm = ({ 
  dashboardForm, 
  handleInputChange, 
  handleAddDashboard, 
  setShowAddForm, 
  loading,
  isEdit = false,
  existingDashboards = []
}) => {
  const [urlValidation, setUrlValidation] = useState({ isValid: true, message: '' })
  const [duplicateNameError, setDuplicateNameError] = useState('')
  
  // Real-time URL validation
  useEffect(() => {
    if (dashboardForm.dashboardUrl) {
      const validation = validateDashboardUrl(dashboardForm.dashboardUrl, dashboardForm.dashboardType)
      setUrlValidation(validation)
    } else {
      setUrlValidation({ isValid: true, message: '' })
    }
  }, [dashboardForm.dashboardUrl, dashboardForm.dashboardType])
  
  // Duplicate name detection
  useEffect(() => {
    if (dashboardForm.dashboardName && !isEdit) {
      const isDuplicate = existingDashboards.some(d => 
        d.dashboardName.toLowerCase() === dashboardForm.dashboardName.toLowerCase()
      )
      setDuplicateNameError(isDuplicate ? 'A dashboard with this name already exists' : '')
    } else {
      setDuplicateNameError('')
    }
  }, [dashboardForm.dashboardName, existingDashboards, isEdit])
  
  const isFormValid = dashboardForm.dashboardName && 
                     dashboardForm.dashboardUrl && 
                     urlValidation.isValid && 
                     !duplicateNameError

  return (
    <div className="dashboard-form">
      <h3>{isEdit ? 'Edit Dashboard' : 'Add Dashboard'}</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-lg)', fontSize: '0.9rem' }}>
        {isEdit ? 'Update your dashboard configuration.' : 'Add a new dashboard to your analytics suite.'}
      </p>
      
      <div className="form-group">
        <label>Dashboard Name *</label>
        <input
          type="text"
          name="dashboardName"
          value={dashboardForm.dashboardName}
          onChange={handleInputChange}
          placeholder="Enter dashboard name (e.g., Sales Analytics)"
          className={duplicateNameError ? 'error' : ''}
        />
        {duplicateNameError && (
          <small className="error-text">{duplicateNameError}</small>
        )}
      </div>
      
      <div className="form-group">
        <label>Dashboard Type *</label>
        <select
          name="dashboardType"
          value={dashboardForm.dashboardType}
          onChange={handleInputChange}
        >
          <option value="looker">Google Looker Studio</option>
          <option value="google_analytics">Google Analytics</option>
          <option value="tableau">Tableau</option>
          <option value="power_bi">Power BI</option>
          <option value="custom">Custom</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Dashboard URL *</label>
        <input
          type="url"
          name="dashboardUrl"
          value={dashboardForm.dashboardUrl}
          onChange={handleInputChange}
          placeholder={getDashboardUrlPlaceholder(dashboardForm.dashboardType)}
          className={!urlValidation.isValid && dashboardForm.dashboardUrl ? 'error' : urlValidation.isValid && dashboardForm.dashboardUrl ? 'success' : ''}
        />
        {dashboardForm.dashboardUrl && (
          <small className={`validation-text ${urlValidation.isValid ? 'success' : 'error'}`}>
            {urlValidation.message}
          </small>
        )}
        <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block' }}>
          {getDashboardUrlHint(dashboardForm.dashboardType)}
        </small>
      </div>
      
      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            name="isActive"
            checked={dashboardForm.isActive}
            onChange={handleInputChange}
          />
          <span className="checkbox-text">Active Dashboard</span>
        </label>
        <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block' }}>
          Only active dashboards will be displayed in the analytics section
        </small>
      </div>
      
      <div className="form-actions">
        <button 
          onClick={handleAddDashboard} 
          disabled={loading || !isFormValid}
          className="btn-primary"
        >
          {loading ? (isEdit ? 'Updating...' : 'Adding...') : (isEdit ? 'Update Dashboard' : 'Add Dashboard')}
        </button>
        <button onClick={() => setShowAddForm(false)} className="btn-secondary">
          Cancel
        </button>
      </div>
    </div>
  )
}

// Helper functions for form
const getDashboardUrlPlaceholder = (type) => {
  switch (type) {
    case 'looker': return 'https://lookerstudio.google.com/embed/reporting/...'
    case 'google_analytics': return 'https://analytics.google.com/...'
    case 'tableau': return 'https://public.tableau.com/...'
    case 'power_bi': return 'https://app.powerbi.com/...'
    default: return 'https://...'
  }
}

const getDashboardUrlHint = (type) => {
  switch (type) {
    case 'looker': return 'Use the embed URL from Google Looker Studio sharing options'
    case 'google_analytics': return 'Use the shareable link from Google Analytics'
    case 'tableau': return 'Use the public or embedded Tableau dashboard URL'
    case 'power_bi': return 'Use the embed or public sharing URL from Power BI'
    default: return 'Enter the dashboard URL that supports embedding'
  }
}

// Edit Dashboard Modal Component
const EditDashboardModal = ({ dashboard, onUpdate, onClose, loading, existingDashboards }) => {
  const [editForm, setEditForm] = useState({
    dashboardName: dashboard.dashboardName,
    dashboardType: dashboard.dashboardType,
    dashboardUrl: dashboard.dashboardUrl,
    isActive: dashboard.isActive
  })

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setEditForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = () => {
    onUpdate(dashboard.id, editForm)
  }

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <DashboardConfigForm
          dashboardForm={editForm}
          handleInputChange={handleInputChange}
          handleAddDashboard={handleSubmit}
          setShowAddForm={onClose}
          loading={loading}
          isEdit={true}
          existingDashboards={existingDashboards.filter(d => d.id !== dashboard.id)}
        />
      </div>
    </div>
  )
}

const AnalyticsDashboard = () => {
  const [dashboards, setDashboards] = useState([])
  const [activeDashboard, setActiveDashboard] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [toasts, setToasts] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [editingDashboard, setEditingDashboard] = useState(null)
  const [selectedDashboards, setSelectedDashboards] = useState(new Set())
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isCustomFullscreen, setIsCustomFullscreen] = useState(false)
  const [isOffline, setIsOffline] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  
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
  
  // Refs for drag and drop
  const draggedItem = useRef(null)
  const dragOverItem = useRef(null)

  useEffect(() => {
    fetchDashboards()
    
    // Online/offline detection
    const handleOnline = () => setIsOffline(false)
    const handleOffline = () => setIsOffline(true)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    // Fullscreen change detection
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    
    // Keyboard shortcuts for custom fullscreen
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isCustomFullscreen) {
        exitCustomFullscreen()
      }
      // Keep old fullscreen for compatibility
      if (e.key === 'Escape' && isFullscreen) {
        exitFullscreen()
      }
    }
    
    document.addEventListener('keydown', handleKeyDown)
    
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isFullscreen, isCustomFullscreen])

  const fetchDashboards = async (retryCount = 0) => {
    try {
      setLoading(true)
      setError(null)
      const response = await getDashboardConfigs()
      setDashboards(response.configs || [])
      
      // Set first active dashboard as default
      const activeConfig = response.configs?.find(d => d.isActive)
      if (activeConfig && !activeDashboard) {
        setActiveDashboard(activeConfig)
      }
    } catch (err) {
      console.error('Failed to fetch dashboards:', err.message)
      
      // Retry mechanism for failed operations
      if (retryCount < 2 && !isOffline) {
        setTimeout(() => fetchDashboards(retryCount + 1), 1000 * (retryCount + 1))
        addToast('Retrying to load dashboards...', 'info')
      } else {
        setError('Failed to load dashboard configurations')
        addToast('Failed to load dashboards', 'error')
      }
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
      addToast('Dashboard added successfully!', 'success')
      
    } catch (err) {
      console.error('Failed to add dashboard:', err.message)
      let errorMessage = 'Failed to add dashboard'
      
      if (err.message.includes('duplicate') || err.message.includes('already exists')) {
        errorMessage = 'A dashboard with this name already exists'
      } else if (err.message.includes('validation')) {
        errorMessage = 'Please check your input and try again'
      } else if (err.message.includes('network') || err.message.includes('fetch')) {
        errorMessage = 'Network error. Please check your connection and try again.'
      }
      
      setError(errorMessage)
      addToast(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDashboard = async (dashboardId) => {
    const dashboard = dashboards.find(d => d.id === dashboardId)
    if (!confirm(`Are you sure you want to delete "${dashboard?.dashboardName}"? This action cannot be undone.`)) return
    
    try {
      setLoading(true)
      const result = await deleteDashboardConfig(dashboardId)
      
      if (result && result.success) {
        setDashboards(prev => prev.filter(d => d.id !== dashboardId))
        
        if (activeDashboard && activeDashboard.id === dashboardId) {
          const remainingDashboards = dashboards.filter(d => d.id !== dashboardId)
          setActiveDashboard(remainingDashboards.length > 0 ? remainingDashboards[0] : null)
        }
        
        // Remove from selection if selected
        setSelectedDashboards(prev => {
          const newSelection = new Set(prev)
          newSelection.delete(dashboardId)
          return newSelection
        })
        
        addToast('Dashboard deleted successfully', 'success')
      } else {
        throw new Error('Delete operation failed')
      }
    } catch (err) {
      console.error('Failed to delete dashboard:', err.message)
      const errorMessage = 'Failed to delete dashboard. Please try again.'
      setError(errorMessage)
      addToast(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Toast management
  const addToast = useCallback((message, type) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  // Update dashboard function
  const handleUpdateDashboard = async (dashboardId, updateData) => {
    try {
      setLoading(true)
      const result = await updateDashboardConfig(dashboardId, updateData)
      
      if (result && result.success) {
        setDashboards(prev => prev.map(d => 
          d.id === dashboardId ? { ...d, ...updateData, updatedAt: result.updatedAt } : d
        ))
        
        // Update active dashboard if it's the one being edited
        if (activeDashboard && activeDashboard.id === dashboardId) {
          setActiveDashboard(prev => ({ ...prev, ...updateData }))
        }
        
        setEditingDashboard(null)
        addToast('Dashboard updated successfully!', 'success')
      } else {
        throw new Error('Update operation failed')
      }
    } catch (err) {
      console.error('Failed to update dashboard:', err.message)
      let errorMessage = 'Failed to update dashboard'
      
      if (err.message.includes('validation')) {
        errorMessage = 'Please check your input and try again'
      } else if (err.message.includes('not found')) {
        errorMessage = 'Dashboard not found or you do not have permission to edit it'
      }
      
      addToast(errorMessage, 'error')
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

  // Bulk operations
  const handleBulkDelete = async () => {
    if (selectedDashboards.size === 0) return
    
    const dashboardNames = Array.from(selectedDashboards)
      .map(id => dashboards.find(d => d.id === id)?.dashboardName)
      .filter(Boolean)
      .join(', ')
    
    if (!confirm(`Are you sure you want to delete ${selectedDashboards.size} dashboard(s)? (${dashboardNames})\n\nThis action cannot be undone.`)) return
    
    try {
      setLoading(true)
      const deletePromises = Array.from(selectedDashboards).map(id => 
        deleteDashboardConfig(id)
      )
      
      await Promise.all(deletePromises)
      
      setDashboards(prev => prev.filter(d => !selectedDashboards.has(d.id)))
      
      // Clear active dashboard if it was deleted
      if (activeDashboard && selectedDashboards.has(activeDashboard.id)) {
        const remainingDashboards = dashboards.filter(d => !selectedDashboards.has(d.id))
        setActiveDashboard(remainingDashboards.length > 0 ? remainingDashboards[0] : null)
      }
      
      setSelectedDashboards(new Set())
      addToast(`${selectedDashboards.size} dashboard(s) deleted successfully`, 'success')
    } catch (err) {
      console.error('Bulk delete failed:', err.message)
      addToast('Failed to delete some dashboards. Please try again.', 'error')
    } finally {
      setLoading(false)
    }
  }

  // Drag and drop handlers
  const handleDragStart = (e, index) => {
    draggedItem.current = index
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragOver = (e, index) => {
    e.preventDefault()
    dragOverItem.current = index
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDragEnd = () => {
    if (draggedItem.current !== null && dragOverItem.current !== null) {
      const newDashboards = [...filteredDashboards]
      const draggedItemContent = newDashboards[draggedItem.current]
      
      // Remove dragged item
      newDashboards.splice(draggedItem.current, 1)
      
      // Insert at new position
      newDashboards.splice(dragOverItem.current, 0, draggedItemContent)
      
      // Update the full dashboards array maintaining the new order
      const reorderedDashboards = dashboards.map(dashboard => {
        const newIndex = newDashboards.findIndex(d => d.id === dashboard.id)
        return newIndex !== -1 ? newDashboards[newIndex] : dashboard
      })
      
      setDashboards(reorderedDashboards)
      addToast('Dashboard order updated', 'success')
    }
    
    draggedItem.current = null
    dragOverItem.current = null
  }

  // Filter and search functionality
  const filteredDashboards = dashboards.filter(dashboard => {
    const matchesSearch = dashboard.dashboardName.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || dashboard.dashboardType === filterType
    const matchesStatus = filterStatus === 'all' || 
      (filterStatus === 'active' && dashboard.isActive) ||
      (filterStatus === 'inactive' && !dashboard.isActive)
    
    return matchesSearch && matchesType && matchesStatus
  })

  // Fullscreen functionality
  const exitFullscreen = () => {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen()
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen()
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen()
    }
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

  // Custom fullscreen implementation
  const handleCustomFullscreen = () => {
    if (isCustomFullscreen) {
      exitCustomFullscreen()
    } else {
      setIsCustomFullscreen(true)
      addToast('Press ESC to exit fullscreen', 'info')
    }
  }

  const exitCustomFullscreen = () => {
    setIsCustomFullscreen(false)
  }

  // Keep old fullscreen for compatibility (fallback)
  const handleFullscreen = async () => {
    const fullscreenContainer = document.querySelector('.dashboard-fullscreen-container')
    if (!fullscreenContainer) {
      addToast('Dashboard container not found', 'error')
      return
    }

    try {
      // Check if already in fullscreen mode
      if (document.fullscreenElement || document.webkitFullscreenElement || 
          document.mozFullScreenElement || document.msFullscreenElement) {
        addToast('Already in fullscreen mode', 'info')
        return
      }

      // Simple container fullscreen approach
      if (fullscreenContainer.requestFullscreen) {
        await fullscreenContainer.requestFullscreen()
      } else if (fullscreenContainer.webkitRequestFullscreen) {
        fullscreenContainer.webkitRequestFullscreen()
      } else if (fullscreenContainer.mozRequestFullScreen) {
        fullscreenContainer.mozRequestFullScreen()
      } else if (fullscreenContainer.msRequestFullscreen) {
        fullscreenContainer.msRequestFullscreen()
      } else {
        addToast('Fullscreen not supported in this browser', 'error')
      }
    } catch (error) {
      console.error('Fullscreen error:', error)
      addToast('Failed to enter fullscreen mode', 'error')
    }
  }

  // Dashboard type icon helper
  const getDashboardTypeIcon = (type) => {
    switch (type) {
      case 'looker': return '📊'
      case 'google_analytics': return '📈'
      case 'tableau': return '📉'
      case 'power_bi': return '💼'
      default: return '🔧'
    }
  }

  // Dashboard type color helper
  const getDashboardTypeColor = (type) => {
    switch (type) {
      case 'looker': return '#4285f4'
      case 'google_analytics': return '#ff7043'
      case 'tableau': return '#1f77b4'
      case 'power_bi': return '#f2c811'
      default: return '#6b7280'
    }
  }


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
      
      console.log('Original URL:', url)
      
      // If it's already an embed URL, return as is
      if (url.includes('/embed/')) {
        console.log('URL already contains /embed/', url)
        return url
      }
      
      // If it's a regular Looker Studio URL, try to convert to embed format
      if (url.includes('lookerstudio.google.com') && url.includes('/reporting/')) {
        const embedUrl = url.replace('/reporting/', '/embed/reporting/')
        console.log('Converted to embed URL:', embedUrl)
        return embedUrl
      }
      
      console.log('URL unchanged:', url)
      return url
    }

    const embedUrl = getEmbedUrl(dashboard.dashboardUrl)

    return (
      <div className="dashboard-viewer-content">
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
              <li>The dashboard requires authentication</li>
            </ul>
            <div style={{ margin: '1rem 0', padding: '0.5rem', background: 'var(--surface-secondary)', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'monospace' }}>
              <strong>Debug Info:</strong><br/>
              Original URL: {dashboard.dashboardUrl}<br/>
              Embed URL: {embedUrl}
            </div>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button onClick={() => window.open(embedUrl, '_blank')} className="viewer-action-btn">
                Open in New Tab
              </button>
              <button onClick={() => {
                console.log('Retrying iframe load for URL:', embedUrl)
                setIframeError(false)
                setIframeLoading(true)
              }} className="viewer-action-btn">
                Retry
              </button>
            </div>
          </div>
        )}
        
        <iframe
          src={embedUrl}
          width="100%"
          height="100%"
          frameBorder="0"
          onLoad={handleIframeLoad}
          onError={handleIframeError}
          className="dashboard-iframe"
          style={{ 
            display: iframeError ? 'none' : 'block',
            borderRadius: '8px',
            border: 'none',
            minHeight: '600px'
          }}
          allow="accelerometer; autoplay; camera; encrypted-media; geolocation; gyroscope; magnetometer; microphone; midi; payment; picture-in-picture; usb"
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-presentation allow-downloads"
          referrerPolicy="strict-origin-when-cross-origin"
          loading="lazy"
          importance="high"
          crossorigin="anonymous"
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
    <>
      {/* Custom Fullscreen Overlay */}
      {isCustomFullscreen && activeDashboard && (
        <div className="custom-fullscreen-overlay">
          <div className="custom-fullscreen-content">
            <DashboardViewer dashboard={activeDashboard} />
          </div>
        </div>
      )}
      
      <div className={`analytics-dashboard-container ${isCustomFullscreen ? 'hidden' : ''}`}>
      <div className={`analytics-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-header-top">
            <button 
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="sidebar-toggle-btn"
              title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>
            {!sidebarCollapsed && <h3>Analytics Dashboards</h3>}
          </div>
          {!sidebarCollapsed && (
            <button 
              onClick={() => setShowAddForm(true)} 
              className="add-dashboard-btn sidebar-add-btn"
              disabled={showAddForm}
            >
              + Add New
            </button>
          )}
          {sidebarCollapsed && (
            <button 
              onClick={() => setShowAddForm(true)} 
              className="add-dashboard-btn sidebar-add-btn collapsed"
              disabled={showAddForm}
              title="Add New Dashboard"
            >
              +
            </button>
          )}
        </div>

        {error && (
          <div className="sidebar-message error">
            {error}
          </div>
        )}

        {success && (
          <div className="sidebar-message success">
            {success}
          </div>
        )}

        {isOffline && (
          <div className="sidebar-message error">
            📡 You are offline. Some features may be limited.
          </div>
        )}

        {/* Search and Filter Controls */}
        {dashboards.length > 0 && (
          <div className="sidebar-controls">
            <div className="search-container">
              <input
                type="text"
                placeholder="Search dashboards..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              <span className="search-icon">🔍</span>
            </div>
            
            <div className="filter-controls">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Types</option>
                <option value="looker">Looker Studio</option>
                <option value="google_analytics">Google Analytics</option>
                <option value="tableau">Tableau</option>
                <option value="power_bi">Power BI</option>
                <option value="custom">Custom</option>
              </select>
              
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            
            {selectedDashboards.size > 0 && (
              <div className="bulk-actions">
                <button
                  onClick={handleBulkDelete}
                  className="bulk-delete-btn"
                  disabled={loading}
                >
                  🗑️ Delete {selectedDashboards.size} selected
                </button>
                <button
                  onClick={() => setSelectedDashboards(new Set())}
                  className="bulk-clear-btn"
                >
                  Clear selection
                </button>
              </div>
            )}
          </div>
        )}

        {filteredDashboards.length === 0 && searchTerm ? (
          <div className="sidebar-empty-state">
            <p>No dashboards match your search</p>
            <button onClick={() => setSearchTerm('')} className="btn-secondary sidebar-empty-btn">
              Clear Search
            </button>
          </div>
        ) : dashboards.length === 0 ? (
          <div className="sidebar-empty-state">
            <p>No dashboards configured</p>
            <button onClick={() => setShowAddForm(true)} className="btn-primary sidebar-empty-btn">
              Add Your First Dashboard
            </button>
          </div>
        ) : (
          <div className="dashboard-list">
            {loading ? (
              <div className="dashboard-loading">
                <div className="skeleton-card"></div>
                <div className="skeleton-card"></div>
                <div className="skeleton-card"></div>
              </div>
            ) : (
              filteredDashboards.map((dashboard, index) => (
                <div 
                  key={dashboard.id}
                  className={`dashboard-card ${activeDashboard?.id === dashboard.id ? 'active' : ''} ${!dashboard.isActive ? 'inactive' : ''}`}
                  onClick={() => setActiveDashboard(dashboard)}
                  draggable
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragEnd={handleDragEnd}
                >
                  <div className="dashboard-card-header">
                    <div className="card-title-section">
                      <div className="card-title-row">
                        <input
                          type="checkbox"
                          checked={selectedDashboards.has(dashboard.id)}
                          onChange={(e) => {
                            e.stopPropagation()
                            const newSelection = new Set(selectedDashboards)
                            if (e.target.checked) {
                              newSelection.add(dashboard.id)
                            } else {
                              newSelection.delete(dashboard.id)
                            }
                            setSelectedDashboards(newSelection)
                          }}
                          className="card-checkbox"
                        />
                        <span className="drag-handle" title="Drag to reorder">⋮⋮</span>
                        {!sidebarCollapsed && <h4>{dashboard.dashboardName}</h4>}
                        {sidebarCollapsed && (
                          <h4 className="dashboard-name-collapsed" title={dashboard.dashboardName}>
                            {dashboard.dashboardName.substring(0, 2).toUpperCase()}
                          </h4>
                        )}
                      </div>
                      {!sidebarCollapsed && (
                        <div className="card-meta">
                          <span className={`status-indicator ${dashboard.isActive ? 'active' : 'inactive'}`}>
                            {dashboard.isActive ? '● Active' : '○ Inactive'}
                          </span>
                        </div>
                      )}
                      {!sidebarCollapsed && dashboard.updatedAt && (
                        <div className="last-updated">
                          Last updated: {new Date(dashboard.updatedAt).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className={`dashboard-card-actions ${sidebarCollapsed ? 'collapsed' : ''}`}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setEditingDashboard(dashboard)
                      }}
                      className="card-action-btn edit"
                      title="Edit dashboard"
                      disabled={loading}
                    >
                      ✏️
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenInLookerStudio(dashboard)
                      }}
                      className="card-action-btn"
                      title="Open dashboard"
                    >
                      🔗
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteDashboard(dashboard.id)
                      }}
                      className="card-action-btn delete"
                      title="Delete dashboard"
                      disabled={loading}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <div className={`analytics-main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {showAddForm && (
          <DashboardConfigForm 
            dashboardForm={dashboardForm}
            handleInputChange={handleInputChange}
            handleAddDashboard={handleAddDashboard}
            setShowAddForm={setShowAddForm}
            loading={loading}
            existingDashboards={dashboards}
          />
        )}

        {!activeDashboard && !showAddForm && dashboards.length > 0 && (
          <div className="dashboard-placeholder">
            <h3>Select a Dashboard</h3>
            <p>Choose a dashboard from the sidebar to view your analytics.</p>
          </div>
        )}

        {!activeDashboard && !showAddForm && dashboards.length === 0 && (
          <div className="dashboard-placeholder">
            <h3>No Dashboards Configured</h3>
            <p>Connect your analytics dashboards to view insights and data visualizations directly in your workspace.</p>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '1rem' }}>
              Supported platforms: Google Looker Studio, Google Analytics, Tableau, Power BI, and custom dashboards.
            </p>
            <button onClick={() => setShowAddForm(true)} className="btn-primary" style={{ marginTop: 'var(--spacing-lg)' }}>
              Add Your First Dashboard
            </button>
          </div>
        )}

        {activeDashboard && !showAddForm && (
          <div className="dashboard-fullscreen-container">
            <div className="dashboard-viewer-container">
              <div className="dashboard-viewer-header">
                <div className="viewer-title">
                  <h2>{activeDashboard.dashboardName}</h2>
                  <div className="dashboard-meta">
                    <span className={`status-badge ${activeDashboard.isActive ? 'active' : 'inactive'}`}>
                      {activeDashboard.isActive ? '● Active' : '○ Inactive'}
                    </span>
                    {activeDashboard.dashboardType === 'looker' && (
                      <span className="refresh-info">Data refreshes automatically every 12 hours</span>
                    )}
                  </div>
                </div>
                <div className="viewer-actions">
                  <button
                    onClick={handleCustomFullscreen}
                    className="viewer-action-btn"
                    title={isCustomFullscreen ? "Exit fullscreen mode (ESC)" : "View dashboard in fullscreen mode (ESC to exit)"}
                  >
                    {isCustomFullscreen ? '⛶ Exit Fullscreen' : '⛶ Fullscreen'}
                  </button>
                  <button
                    onClick={() => setEditingDashboard(activeDashboard)}
                    className="viewer-action-btn"
                    title="Edit dashboard settings"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => handleOpenInLookerStudio(activeDashboard)}
                    className="viewer-action-btn primary"
                    title="Open in external platform"
                  >
                    🔗 Open External
                  </button>
                </div>
              </div>
              <DashboardViewer dashboard={activeDashboard} />
            </div>
          </div>
        )}

        {/* Edit Dashboard Modal */}
        {editingDashboard && (
          <EditDashboardModal
            dashboard={editingDashboard}
            onUpdate={handleUpdateDashboard}
            onClose={() => setEditingDashboard(null)}
            loading={loading}
            existingDashboards={dashboards}
          />
        )}

        {/* Toast Notifications */}
        <div className="toast-container">
          {toasts.map(toast => (
            <Toast
              key={toast.id}
              message={toast.message}
              type={toast.type}
              onClose={() => removeToast(toast.id)}
            />
          ))}
        </div>
      </div>
    </div>
    </>
  )
}

export default AnalyticsDashboard