import React, { useState, useEffect } from 'react'
import apiService from '../services/api'

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showPassword, setShowPassword] = useState(false)
  const [isEmailFocused, setIsEmailFocused] = useState(false)
  const [isPasswordFocused, setIsPasswordFocused] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

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
      {/* Animated Background Elements */}
      <div className="background-elements">
        <div className="floating-particles">
          {[...Array(12)].map((_, i) => (
            <div 
              key={i} 
              className={`particle particle-${i + 1} ${mounted ? 'animate' : ''}`}
              style={{
                '--delay': `${i * 0.8}s`,
                '--duration': `${8 + (i % 4) * 2}s`
              }}
            />
          ))}
        </div>
        <div className="gradient-orbs">
          <div className="orb orb-1"></div>
          <div className="orb orb-2"></div>
          <div className="orb orb-3"></div>
        </div>
      </div>
      
      <div className="taskifai-login-box">
        {/* Enhanced TaskifAI Logo */}
        <div className="login-header">
          <div className={`login-logo ${mounted ? 'animate-in' : ''}`}>
            <div className="logo-icon-container">
              <div className="logo-icon">
                <span className="logo-letter">T</span>
                <div className="logo-pulse"></div>
              </div>
            </div>
            <span className="logo-text">
              <span className="text-primary">Taskif</span>
              <span className="text-accent">AI</span>
            </span>
          </div>
          <div className={`login-tagline ${mounted ? 'animate-in' : ''}`}>
            <div className="sparkles">
              <span className="sparkle sparkle-1">✨</span>
              <span className="sparkle sparkle-2">✨</span>
              <span className="sparkle sparkle-3">✨</span>
            </div>
          </div>
        </div>
        
        {/* Login Form */}
        <div className="login-form-container">
          <h2>Welcome back</h2>
          <p className="form-subtitle">Sign in to access your data insights</p>
          
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <div className="input-container">
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onFocus={() => setIsEmailFocused(true)}
                  onBlur={() => setIsEmailFocused(false)}
                  required
                  className="taskifai-input"
                  aria-label="Email address"
                />
                <label 
                  htmlFor="email" 
                  className={`floating-label ${isEmailFocused || email ? 'focused' : ''}`}
                >
                  Email address
                </label>
                <div className="input-highlight"></div>
              </div>
            </div>

            <div className="form-group">
              <div className="input-container">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onFocus={() => setIsPasswordFocused(true)}
                  onBlur={() => setIsPasswordFocused(false)}
                  required
                  className="taskifai-input"
                  aria-label="Password"
                />
                <label 
                  htmlFor="password" 
                  className={`floating-label ${isPasswordFocused || password ? 'focused' : ''}`}
                >
                  Password
                </label>
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  <span className={`eye-icon ${showPassword ? 'open' : 'closed'}`}>
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </span>
                </button>
                <div className="input-highlight"></div>
              </div>
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
          background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
          padding: var(--space-8);
          position: relative;
          overflow: hidden;
        }

        /* Enhanced Background Elements */
        .background-elements {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
          z-index: 0;
        }

        .floating-particles {
          position: absolute;
          width: 100%;
          height: 100%;
        }

        .particle {
          position: absolute;
          background: var(--gradient-primary);
          border-radius: 50%;
          opacity: 0;
          transition: opacity 0.5s ease-in-out;
        }

        .particle.animate {
          opacity: 0.4;
          animation: float var(--duration, 10s) var(--delay, 0s) infinite ease-in-out;
        }

        .particle-1 { width: 8px; height: 8px; top: 15%; left: 10%; }
        .particle-2 { width: 12px; height: 12px; top: 25%; right: 15%; }
        .particle-3 { width: 6px; height: 6px; top: 35%; left: 20%; }
        .particle-4 { width: 10px; height: 10px; top: 45%; right: 25%; }
        .particle-5 { width: 14px; height: 14px; top: 55%; left: 15%; }
        .particle-6 { width: 8px; height: 8px; top: 65%; right: 20%; }
        .particle-7 { width: 12px; height: 12px; top: 75%; left: 25%; }
        .particle-8 { width: 6px; height: 6px; top: 85%; right: 10%; }
        .particle-9 { width: 10px; height: 10px; top: 20%; left: 80%; }
        .particle-10 { width: 8px; height: 8px; top: 60%; left: 85%; }
        .particle-11 { width: 12px; height: 12px; top: 40%; left: 75%; }
        .particle-12 { width: 14px; height: 14px; top: 80%; left: 70%; }

        .gradient-orbs {
          position: absolute;
          width: 100%;
          height: 100%;
        }

        .orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(60px);
          opacity: 0.3;
          animation: pulse 4s infinite ease-in-out;
        }

        .orb-1 {
          width: 200px;
          height: 200px;
          background: var(--gradient-primary);
          top: 10%;
          left: 10%;
          animation-delay: 0s;
        }

        .orb-2 {
          width: 150px;
          height: 150px;
          background: var(--gradient-secondary);
          bottom: 20%;
          right: 15%;
          animation-delay: 1.5s;
        }

        .orb-3 {
          width: 180px;
          height: 180px;
          background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-300) 100%);
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          animation-delay: 3s;
        }

        .taskifai-login-box {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(20px) saturate(1.8);
          padding: var(--space-16);
          border-radius: 32px;
          box-shadow: 
            0 32px 64px rgba(0, 47, 167, 0.12),
            0 8px 32px rgba(0, 47, 167, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
          width: 100%;
          max-width: 480px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          position: relative;
          z-index: 1;
          text-align: center;
          transform: translateY(20px);
          opacity: 0;
          animation: slideInUp 0.8s ease-out 0.2s forwards;
        }

        .taskifai-login-box::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
          border-radius: 32px;
          pointer-events: none;
        }

        .login-header {
          margin-bottom: var(--space-12);
        }

        /* Enhanced Logo Animations */
        .login-logo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--space-4);
          margin-bottom: var(--space-10);
          transform: translateY(30px);
          opacity: 0;
        }

        .login-logo.animate-in {
          animation: fadeInUp 0.8s ease-out 0.4s forwards;
        }

        .logo-icon-container {
          position: relative;
        }

        .logo-icon {
          width: 80px;
          height: 80px;
          background: var(--gradient-primary);
          border-radius: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 2.5rem;
          font-weight: var(--font-extrabold);
          box-shadow: 
            0 20px 40px rgba(0, 47, 167, 0.3),
            0 4px 12px rgba(0, 47, 167, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
          border: 2px solid rgba(255, 255, 255, 0.2);
          position: relative;
          overflow: hidden;
          transition: transform 0.3s ease;
        }

        .logo-icon:hover {
          transform: scale(1.05) rotate(2deg);
        }

        .logo-letter {
          position: relative;
          z-index: 2;
          animation: breathe 3s ease-in-out infinite;
        }

        .logo-pulse {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 100%;
          height: 100%;
          background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
          border-radius: 50%;
          animation: pulse 2s ease-in-out infinite;
        }

        .logo-text {
          font-family: var(--font-display);
          font-size: 3rem;
          font-weight: var(--font-extrabold);
          text-transform: uppercase;
          letter-spacing: 0.1em;
          margin-left: var(--space-2);
        }

        .text-primary {
          background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-500) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: shimmer 3s ease-in-out infinite;
        }

        .text-accent {
          background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-300) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: shimmer 3s ease-in-out infinite 1.5s;
        }

        .login-tagline {
          transform: translateY(30px);
          opacity: 0;
          position: relative;
        }

        .login-tagline.animate-in {
          animation: fadeInUp 0.8s ease-out 0.6s forwards;
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

        .sparkles {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
        }

        .sparkle {
          position: absolute;
          font-size: 1.2rem;
          opacity: 0;
          animation: sparkle 2s ease-in-out infinite;
        }

        .sparkle-1 {
          top: 10%;
          left: 80%;
          animation-delay: 0s;
        }

        .sparkle-2 {
          top: 60%;
          left: 15%;
          animation-delay: 0.7s;
        }

        .sparkle-3 {
          top: 30%;
          right: 10%;
          animation-delay: 1.4s;
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
          gap: var(--space-8);
        }

        /* Enhanced Form Groups */
        .form-group {
          position: relative;
        }

        .input-container {
          position: relative;
          display: flex;
          flex-direction: column;
        }

        /* Floating Label System */
        .floating-label {
          position: absolute;
          left: 16px;
          top: 50%;
          transform: translateY(-50%);
          background: transparent;
          color: var(--text-secondary);
          font-size: var(--text-base);
          font-weight: var(--font-medium);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          pointer-events: none;
          z-index: 2;
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .floating-label.focused {
          top: -8px;
          left: 12px;
          font-size: var(--text-xs);
          color: var(--primary-600);
          background: rgba(255, 255, 255, 0.9);
          padding: 0 8px;
          transform: translateY(0);
        }

        /* Enhanced Input Styles */
        .taskifai-input {
          padding: 20px 16px 12px 16px;
          border: 2px solid #e2e8f0;
          border-radius: 16px;
          font-size: var(--text-base);
          font-family: var(--font-sans);
          background: rgba(255, 255, 255, 0.8);
          color: var(--text-primary);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          z-index: 1;
          width: 100%;
          box-shadow: 
            0 1px 3px rgba(0, 47, 167, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }

        .taskifai-input:focus {
          outline: none;
          border-color: var(--primary-600);
          box-shadow: 
            0 0 0 4px rgba(0, 47, 167, 0.1),
            0 4px 12px rgba(0, 47, 167, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
          background: rgba(255, 255, 255, 0.95);
          transform: scale(1.02);
        }

        .taskifai-input::placeholder {
          color: transparent;
        }

        /* Input Highlight Effect */
        .input-highlight {
          position: absolute;
          bottom: 0;
          left: 50%;
          width: 0;
          height: 2px;
          background: var(--gradient-primary);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          transform: translateX(-50%);
          border-radius: 1px;
        }

        .input-container:focus-within .input-highlight {
          width: 100%;
        }

        /* Password Toggle Styles */
        .password-toggle {
          position: absolute;
          right: 16px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          border-radius: 8px;
          transition: all 0.2s ease;
          z-index: 3;
        }

        .password-toggle:hover {
          background: rgba(0, 47, 167, 0.1);
          transform: translateY(-50%) scale(1.1);
        }

        .eye-icon {
          font-size: 1.2rem;
          transition: transform 0.2s ease;
          display: inline-block;
        }

        .eye-icon.open {
          transform: scale(1.1);
        }

        .eye-icon.closed {
          opacity: 0.7;
        }

        /* Enhanced Error Styles */
        .taskifai-error {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
          color: var(--error-500);
          padding: 16px 20px;
          border-radius: 16px;
          border: 2px solid rgba(239, 68, 68, 0.2);
          font-size: var(--text-sm);
          margin: var(--space-4) 0;
          font-weight: var(--font-medium);
          backdrop-filter: blur(10px);
          animation: slideInDown 0.3s ease-out;
          box-shadow: 
            0 4px 12px rgba(239, 68, 68, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        .error-icon {
          font-size: 1.25rem;
          animation: shake 0.5s ease-in-out;
        }

        /* Enhanced Button Styles */
        .taskifai-login-btn {
          width: 100%;
          padding: 20px 32px;
          background: var(--gradient-primary);
          color: white;
          border: none;
          border-radius: 16px;
          font-size: var(--text-base);
          font-weight: var(--font-semibold);
          font-family: var(--font-sans);
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--space-3);
          margin-top: var(--space-8);
          box-shadow: 
            0 8px 24px rgba(0, 47, 167, 0.25),
            0 4px 12px rgba(0, 47, 167, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          position: relative;
          overflow: hidden;
        }

        .taskifai-login-btn::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s;
        }

        .taskifai-login-btn:hover:not(:disabled) {
          background: var(--gradient-secondary);
          transform: translateY(-2px) scale(1.02);
          box-shadow: 
            0 12px 32px rgba(0, 47, 167, 0.3),
            0 8px 16px rgba(0, 47, 167, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        .taskifai-login-btn:hover:not(:disabled)::before {
          left: 100%;
        }

        .taskifai-login-btn:active {
          transform: translateY(0) scale(1);
        }

        .taskifai-login-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .taskifai-login-btn:disabled::before {
          display: none;
        }

        .btn-arrow {
          font-size: 1.5rem;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          display: inline-block;
        }

        .taskifai-login-btn:hover:not(:disabled) .btn-arrow {
          transform: translateX(6px) scale(1.1);
        }

        /* Enhanced Loading Spinner */
        .loading-spinner {
          width: 20px;
          height: 20px;
          border: 3px solid rgba(255, 255, 255, 0.3);
          border-top: 3px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }

        /* Enhanced Footer */
        .login-footer {
          margin-top: var(--space-12);
          padding-top: var(--space-8);
          border-top: 1px solid rgba(0, 47, 167, 0.1);
          text-align: center;
          position: relative;
        }

        .login-footer::before {
          content: '';
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 60px;
          height: 1px;
          background: var(--gradient-primary);
        }

        .login-footer p {
          font-size: var(--text-xs);
          color: var(--text-muted);
          margin: 0;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          font-weight: var(--font-medium);
          opacity: 0.8;
        }

        /* Enhanced Keyframe Animations */
        @keyframes float {
          0%, 100% { 
            transform: translateY(0px) rotate(0deg);
            opacity: 0.4;
          }
          33% { 
            transform: translateY(-20px) rotate(120deg);
            opacity: 0.6;
          }
          66% { 
            transform: translateY(10px) rotate(240deg);
            opacity: 0.3;
          }
        }

        @keyframes pulse {
          0%, 100% { 
            transform: scale(1);
            opacity: 0.3;
          }
          50% { 
            transform: scale(1.1);
            opacity: 0.5;
          }
        }

        @keyframes slideInUp {
          0% {
            transform: translateY(30px);
            opacity: 0;
          }
          100% {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes fadeInUp {
          0% {
            transform: translateY(30px);
            opacity: 0;
          }
          100% {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes breathe {
          0%, 100% { 
            transform: scale(1);
          }
          50% { 
            transform: scale(1.05);
          }
        }

        @keyframes shimmer {
          0% {
            background-position: -200% center;
          }
          100% {
            background-position: 200% center;
          }
        }

        @keyframes sparkle {
          0%, 100% { 
            opacity: 0;
            transform: scale(0.8);
          }
          50% { 
            opacity: 1;
            transform: scale(1.2);
          }
        }

        @keyframes slideInDown {
          0% {
            transform: translateY(-20px);
            opacity: 0;
          }
          100% {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-4px); }
          75% { transform: translateX(4px); }
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        /* Enhanced Mobile Responsiveness */
        @media (max-width: 768px) {
          .taskifai-login-container {
            padding: 1rem;
          }

          .taskifai-login-box {
            padding: 2rem;
            max-width: 100%;
            border-radius: 24px;
          }

          .login-tagline h1 {
            font-size: 1.5rem;
          }

          .logo-text {
            font-size: 2rem;
          }

          .logo-icon {
            width: 64px;
            height: 64px;
            font-size: 2rem;
          }

          .particle {
            display: none; /* Hide particles on mobile for better performance */
          }

          .orb {
            filter: blur(40px);
          }

          .taskifai-login-btn {
            padding: 18px 28px;
            font-size: 0.9rem;
          }

          /* Touch-friendly interactions */
          .password-toggle {
            padding: 12px;
            right: 12px;
          }

          .taskifai-input {
            padding: 18px 16px 12px 16px;
          }
        }

        @media (max-width: 480px) {
          .taskifai-login-box {
            padding: 1.5rem;
            border-radius: 20px;
          }

          .login-tagline h1 {
            font-size: 1.25rem;
          }

          .login-tagline p {
            font-size: 0.9rem;
          }

          .logo-text {
            font-size: 1.75rem;
          }

          .logo-icon {
            width: 56px;
            height: 56px;
            font-size: 1.75rem;
          }

          .taskifai-login-btn {
            padding: 16px 24px;
            font-size: 0.85rem;
          }
        }

        /* Accessibility Enhancements */
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
          
          .particle, .orb {
            animation: none;
          }
          
          .sparkle {
            display: none;
          }
        }

        /* High contrast mode support */
        @media (prefers-contrast: high) {
          .taskifai-login-box {
            border: 3px solid #000;
            background: #fff;
            backdrop-filter: none;
          }
          
          .taskifai-input {
            border: 2px solid #000;
            background: #fff;
          }
          
          .floating-label.focused {
            color: #000;
            background: #fff;
          }
        }

        /* Focus-visible for better keyboard navigation */
        .taskifai-input:focus-visible,
        .password-toggle:focus-visible,
        .taskifai-login-btn:focus-visible {
          outline: 3px solid var(--primary-600);
          outline-offset: 2px;
        }
      `}</style>
    </div>
  )
}

export default Login