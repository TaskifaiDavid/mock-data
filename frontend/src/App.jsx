import React, { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        setLoading(false)
        return
      }

      // Validate token with backend
      const response = await fetch('http://localhost:8000/api/auth/debug-token', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const debugInfo = await response.json()

      if (debugInfo.user_found) {
        setIsAuthenticated(true)
        setUser({
          email: debugInfo.user_email,
          id: debugInfo.user_id
        })
      } else {
        // Invalid token, clear it
        localStorage.removeItem('access_token')
        setIsAuthenticated(false)
      }
    } catch (error) {
      // Keep essential error logging for production debugging
      console.error('Authentication check failed:', error.message)
      localStorage.removeItem('access_token')
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }

  // Handle route changes from login
  useEffect(() => {
    const handleStorageChange = () => {
      checkAuthStatus()
    }
    
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="app">
      {!isAuthenticated ? (
        <Login onLoginSuccess={checkAuthStatus} />
      ) : (
        <Dashboard user={user} onLogout={() => {
          localStorage.removeItem('access_token')
          setIsAuthenticated(false)
          setUser(null)
        }} />
      )}
    </div>
  )
}

export default App