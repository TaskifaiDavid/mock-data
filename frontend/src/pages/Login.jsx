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
      // Clear any existing stale tokens before login attempt
      localStorage.removeItem('access_token')
      
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
      
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || `Login failed (${response.status})`)
      }

      // Store the access token for API calls
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token)
        
        // Small delay to ensure token is stored before validation
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // Trigger auth check in parent component
        if (onLoginSuccess) {
          onLoginSuccess()
        }
      } else {
        throw new Error('No access token received')
      }
    } catch (error) {
      // Provide more specific error messages for production
      let errorMessage = error.message
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Unable to connect to server. Please check if the backend is running on http://localhost:8000'
      } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
        errorMessage = 'Network error: Cannot reach the login server'
      }
      
      setError(errorMessage)
      // Keep essential error logging for production debugging
      console.error('Login failed:', errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="taskifai-login-container">
      <div className="taskifai-login-box">
        {/* TaskifAI Logo */}
        <div className="login-header">
          <div className="login-logo">
            <div className="logo-icon">T</div>
            <span className="logo-text">TaskifAI</span>
          </div>
          <div className="login-tagline">
            <h1>From chaos to clarity - instantly</h1>
            <p>Transform your data with AI-powered analytics</p>
          </div>
        </div>
        
        {/* Login Form */}
        <div className="login-form-container">
          <h2>Welcome back</h2>
          <p className="form-subtitle">Sign in to access your data insights</p>
          
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email"
                className="taskifai-input"
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
                className="taskifai-input"
              />
            </div>

            {error && (
              <div className="taskifai-error">
                <span className="error-icon">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <button type="submit" disabled={loading} className="taskifai-login-btn">
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <span className="btn-arrow">→</span>
                </>
              )}
            </button>
          </form>
          
          {/* Additional Info */}
          <div className="login-footer">
            <p>Secure, fast, and intelligent data processing</p>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .taskifai-login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bibbi-background);
          padding: var(--space-8);
          position: relative;
          overflow: hidden;
        }

        .taskifai-login-container::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(circle at 25% 25%, var(--primary-50) 0%, transparent 50%),
                      radial-gradient(circle at 75% 75%, var(--primary-100) 0%, transparent 50%);
          opacity: 0.7;
          pointer-events: none;
        }

        .taskifai-login-box {
          background: var(--surface-glass-strong);
          backdrop-filter: var(--glass-backdrop);
          padding: var(--space-16);
          border-radius: var(--radius-2xl);
          box-shadow: var(--shadow-2xl);
          width: 100%;
          max-width: var(--max-width-md);
          border: 1px solid var(--glass-border);
          position: relative;
          z-index: 1;
          text-align: center;
        }

        .login-header {
          margin-bottom: var(--space-12);
        }

        .login-logo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--space-4);
          margin-bottom: var(--space-10);
        }

        .logo-icon {
          width: 64px;
          height: 64px;
          background: var(--gradient-primary);
          border-radius: var(--radius-xl);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-on-primary);
          font-size: var(--text-2xl);
          font-weight: var(--font-extrabold);
          box-shadow: var(--shadow-lg);
          border: 2px solid var(--glass-border);
        }

        .logo-text {
          font-family: var(--font-display);
          font-size: var(--text-4xl);
          font-weight: var(--font-extrabold);
          background: var(--gradient-text);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }

        .login-tagline h1 {
          font-family: var(--font-display);
          font-size: var(--text-2xl);
          font-weight: var(--font-bold);
          color: var(--text-primary);
          margin: 0 0 var(--space-3) 0;
          letter-spacing: 0.02em;
          line-height: var(--leading-tight);
          text-transform: uppercase;
        }

        .login-tagline p {
          font-size: var(--text-base);
          color: var(--text-secondary);
          margin: 0;
          font-weight: var(--font-normal);
          line-height: var(--leading-relaxed);
        }

        .login-form-container {
          text-align: left;
        }

        .login-form-container h2 {
          font-family: var(--font-display);
          font-size: var(--text-xl);
          font-weight: var(--font-semibold);
          color: var(--text-primary);
          margin: 0 0 var(--space-2) 0;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .form-subtitle {
          font-size: var(--text-sm);
          color: var(--text-secondary);
          margin: 0 0 var(--space-12) 0;
          font-weight: var(--font-normal);
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: var(--space-6);
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
        }

        .form-group label {
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
          color: var(--text-primary);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .taskifai-input {
          padding: var(--space-4);
          border: 1px solid var(--border-medium);
          border-radius: var(--radius-lg);
          font-size: var(--text-base);
          font-family: var(--font-sans);
          background-color: var(--surface-primary);
          color: var(--text-primary);
          transition: all var(--duration-150) var(--ease-out);
        }

        .taskifai-input:focus {
          outline: none;
          border-color: var(--border-focus);
          box-shadow: 0 0 0 3px var(--primary-100);
        }

        .taskifai-input::placeholder {
          color: var(--text-muted);
        }

        .taskifai-error {
          display: flex;
          align-items: center;
          gap: var(--space-2);
          background-color: #FEF2F2;
          color: var(--error-500);
          padding: var(--space-4);
          border-radius: var(--radius-lg);
          border: 1px solid #FECACA;
          font-size: var(--text-sm);
          margin: var(--space-4) 0;
        }

        .error-icon {
          font-size: var(--text-lg);
        }

        .taskifai-login-btn {
          width: 100%;
          padding: var(--space-4) var(--space-6);
          background: var(--gradient-primary);
          color: var(--text-on-primary);
          border: none;
          border-radius: var(--radius-lg);
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
          font-family: var(--font-sans);
          cursor: pointer;
          transition: all var(--duration-200) var(--ease-out);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--space-2);
          margin-top: var(--space-6);
          box-shadow: var(--shadow-md);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .taskifai-login-btn:hover:not(:disabled) {
          background: var(--gradient-secondary);
          transform: translateY(-1px);
          box-shadow: var(--shadow-lg);
        }

        .taskifai-login-btn:active {
          transform: translateY(0);
        }

        .taskifai-login-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .btn-arrow {
          font-size: 1.25rem;
          transition: transform 0.2s ease;
        }

        .taskifai-login-btn:hover:not(:disabled) .btn-arrow {
          transform: translateX(4px);
        }

        .loading-spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .login-footer {
          margin-top: var(--space-12);
          padding-top: var(--space-8);
          border-top: 1px solid var(--border-light);
          text-align: center;
        }

        .login-footer p {
          font-size: var(--text-xs);
          color: var(--text-muted);
          margin: 0;
          text-transform: uppercase;
          letter-spacing: 0.025em;
          font-weight: var(--font-medium);
        }

        @keyframes gradientShift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .taskifai-login-container {
            padding: 1rem;
          }

          .taskifai-login-box {
            padding: 2rem;
            max-width: 100%;
          }

          .login-tagline h1 {
            font-size: 1.5rem;
          }

          .logo-text {
            font-size: 1.875rem;
          }

          .logo-icon {
            width: 48px;
            height: 48px;
            font-size: 24px;
          }
        }

        @media (max-width: 480px) {
          .taskifai-login-box {
            padding: 1.5rem;
          }

          .login-tagline h1 {
            font-size: 1.25rem;
          }

          .login-tagline p {
            font-size: 0.9rem;
          }
        }
      `}</style>
    </div>
  )
}

export default Login