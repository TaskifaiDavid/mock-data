const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token')
    
    console.log('API Request:', {
      endpoint,
      hasToken: !!token,
      tokenLength: token ? token.length : 0,
      tokenPreview: token ? `${token.substring(0, 20)}...` : 'none'
    })
    
    const config = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': token ? `Bearer ${token}` : '',
      },
    }

    const response = await fetch(`${API_URL}${endpoint}`, config)
    
    if (!response.ok) {
      console.error('API Error:', {
        status: response.status,
        statusText: response.statusText,
        endpoint
      })
      
      // Handle authentication errors specifically
      if (response.status === 401) {
        console.warn('Authentication failed - clearing token')
        localStorage.removeItem('access_token')
        // Redirect to login or trigger auth refresh
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      
      try {
        const error = await response.json()
        throw new Error(error.error || `Request failed with status ${response.status}`)
      } catch (parseError) {
        throw new Error(`Request failed with status ${response.status}`)
      }
    }

    return response.json()
  }

  async uploadFile(file) {
    const token = localStorage.getItem('access_token')
    console.log('Upload File:', {
      fileName: file.name,
      hasToken: !!token,
      tokenLength: token ? token.length : 0
    })
    
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
      console.error('Upload Error:', {
        status: response.status,
        statusText: response.statusText
      })
      
      if (response.status === 401) {
        console.warn('Upload authentication failed - clearing token')
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

  async getStatus(uploadId) {
    return this.request(`/api/status/${uploadId}`)
  }

  async getUserUploads() {
    return this.request('/api/status/uploads')
  }
}

export default new ApiService()