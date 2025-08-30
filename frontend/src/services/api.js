const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token')
    
    const config = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': token ? `Bearer ${token}` : '',
      },
    }

    let response
    try {
      response = await fetch(`${API_URL}${endpoint}`, config)
    } catch (fetchError) {
      // Keep essential network error logging
      console.error('Network error:', fetchError.message)
      throw new Error(`Network error: ${fetchError.message}`)
    }
    
    if (!response.ok) {
      // Handle authentication errors specifically
      if (response.status === 401) {
        localStorage.removeItem('access_token')
        // Redirect to login or trigger auth refresh
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      
      try {
        const error = await response.json()
        // Enhanced error message handling
        let errorMessage = error.error || error.detail || `Request failed with status ${response.status}`
        
        // Handle validation errors from Pydantic
        if (error.detail && Array.isArray(error.detail)) {
          errorMessage = error.detail.map(err => err.msg || err.message).join(', ')
        }
        
        throw new Error(errorMessage)
      } catch (parseError) {
        // Handle cases where response is not JSON
        const statusMessages = {
          400: 'Bad request. Please check your input.',
          403: 'You do not have permission to perform this action.',
          404: 'The requested resource was not found.',
          409: 'A conflict occurred. The resource may already exist.',
          422: 'Validation error. Please check your input.',
          500: 'Internal server error. Please try again later.',
          503: 'Service temporarily unavailable. Please try again later.'
        }
        
        const message = statusMessages[response.status] || `Request failed with status ${response.status}`
        throw new Error(message)
      }
    }

    return response.json()
  }

  async uploadFile(file) {
    const token = localStorage.getItem('access_token')
    
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_URL}/api/upload/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    })

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      
      try {
        const error = await response.json()
        throw new Error(error.error || 'Upload failed')
      } catch (parseError) {
        throw new Error(`Upload failed with status ${response.status}`)
      }
    }

    return response.json()
  }

  async uploadMultipleFiles(files) {
    const token = localStorage.getItem('access_token')
    
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await fetch(`${API_URL}/api/upload/multiple`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    })

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      
      try {
        const error = await response.json()
        throw new Error(error.error || 'Multiple upload failed')
      } catch (parseError) {
        throw new Error(`Multiple upload failed with status ${response.status}`)
      }
    }

    return response.json()
  }

  async getStatus(uploadId) {
    return this.request(`/api/status/${uploadId}`)
  }

  async getUserUploads() {
    return this.request('/api/status/uploads')
  }

  // Email and Reporting methods
  async generateReport(reportRequest) {
    return this.request('/api/reports/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reportRequest),
    })
  }

  async sendReportEmail(emailRequest) {
    return this.request('/api/reports/email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(emailRequest),
    })
  }

  async sendNotificationEmail(emailRequest) {
    return this.request('/api/email/notification', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(emailRequest),
    })
  }

  async getEmailLogs(limit = 50, offset = 0) {
    return this.request(`/api/email/logs?limit=${limit}&offset=${offset}`)
  }


  // Dashboard methods
  async getDashboardConfigs() {
    return this.request('/api/dashboards/configs')
  }

  async saveDashboardConfig(config) {
    return this.request('/api/dashboards/configs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
  }

  async updateDashboardConfig(configId, config) {
    return this.request(`/api/dashboards/configs/${configId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
  }

  async deleteDashboardConfig(configId) {
    return this.request(`/api/dashboards/configs/${configId}`, {
      method: 'DELETE',
    })
  }
}

const apiService = new ApiService()

// Export individual methods with proper this binding
export const uploadFile = apiService.uploadFile.bind(apiService)
export const uploadMultipleFiles = apiService.uploadMultipleFiles.bind(apiService)
export const getStatus = apiService.getStatus.bind(apiService)
export const getUserUploads = apiService.getUserUploads.bind(apiService)
export const generateReport = apiService.generateReport.bind(apiService)
export const sendReportEmail = apiService.sendReportEmail.bind(apiService)
export const sendNotificationEmail = apiService.sendNotificationEmail.bind(apiService)
export const getEmailLogs = apiService.getEmailLogs.bind(apiService)
export const getDashboardConfigs = apiService.getDashboardConfigs.bind(apiService)
export const saveDashboardConfig = apiService.saveDashboardConfig.bind(apiService)
export const updateDashboardConfig = apiService.updateDashboardConfig.bind(apiService)
export const deleteDashboardConfig = apiService.deleteDashboardConfig.bind(apiService)

export default apiService