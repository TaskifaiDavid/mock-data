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

    const response = await fetch(`${API_URL}${endpoint}`, config)
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Request failed')
    }

    return response.json()
  }

  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_URL}/api/upload/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Upload failed')
    }

    return response.json()
  }

  async getStatus(uploadId) {
    return this.request(`/api/status/${uploadId}`)
  }
}

export default new ApiService()