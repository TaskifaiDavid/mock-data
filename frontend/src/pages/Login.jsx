import React, { useState } from 'react'
import apiService from '../services/api'

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      console.log('Attempting login with backend API...')
      
      // Use backend API for login (direct connection)
      // Alternative: Use '/api/auth/login' for Vite proxy if direct connection fails
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', Object.fromEntries(response.headers.entries()))
      
      const data = await response.json()
      console.log('Response data:', data)

      if (!response.ok) {
        console.error('Login failed with status:', response.status)
        console.error('Error data:', data)
        throw new Error(data.error || data.detail || `Login failed (${response.status})`)
      }

      console.log('Login successful:', { 
        hasToken: !!data.access_token,
        tokenLength: data.access_token?.length,
        userEmail: data.user?.email 
      })

      // Store the access token for API calls
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token)
        console.log('Token stored in localStorage')
        
        // Trigger auth check in parent component
        if (onLoginSuccess) {
          onLoginSuccess()
        }
      } else {
        throw new Error('No access token received')
      }
    } catch (error) {
      console.error('Login error details:', {
        message: error.message,
        name: error.name,
        stack: error.stack
      })
      
      // Provide more specific error messages
      let errorMessage = error.message
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Unable to connect to server. Please check if the backend is running on http://localhost:8000'
      } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
        errorMessage = 'Network error: Cannot reach the login server'
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>TaskifAI</h1>
        <h2>Smart Data Pipeline</h2>
        
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login