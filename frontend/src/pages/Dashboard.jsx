import React, { useState } from 'react'
import Upload from '../components/Upload'
import StatusList from '../components/StatusList'
import AnalyticsDashboard from '../components/AnalyticsDashboard'
import ChatSection from '../components/ChatSection'
import LandingPage from '../components/LandingPage'

function Dashboard({ user, onLogout }) {
  const [activeView, setActiveView] = useState('landing')

  const handleLogout = () => {
    if (onLogout) {
      onLogout()
    }
  }

  const handleLandingNavigation = (view) => {
    setActiveView(view)
  }

  return (
    <div className="taskifai-dashboard">
      {activeView !== 'landing' && (
        <header className="taskifai-header">
          <div className="header-left">
            <div 
              className="taskifai-brand"
              onClick={() => setActiveView('landing')}
              style={{ cursor: 'pointer' }}
            >
              <div className="brand-icon">T</div>
              <div className="brand-text">
                <h1>TaskifAI</h1>
              </div>
            </div>
          </div>
          
          <nav className="taskifai-nav">
            <button
              className={`nav-item ${activeView === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveView('upload')}
            >
              <span className="nav-icon">📊</span>
              <span className="nav-text">Upload Data</span>
            </button>
            <button
              className={`nav-item ${activeView === 'status' ? 'active' : ''}`}
              onClick={() => setActiveView('status')}
            >
              <span className="nav-icon">⚡</span>
              <span className="nav-text">Status</span>
            </button>
            <button
              className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveView('chat')}
            >
              <span className="nav-icon">🤖</span>
              <span className="nav-text">AI Assistant</span>
            </button>
            <button
              className={`nav-item ${activeView === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveView('analytics')}
            >
              <span className="nav-icon">🔍</span>
              <span className="nav-text">Analytics</span>
            </button>
          </nav>

          <div className="header-user">
            <div className="user-profile">
              <div className="user-avatar">
                {(user?.email?.[0] || 'U').toUpperCase()}
              </div>
              <div className="user-details">
                <span className="user-email">{user?.email || 'Unknown User'}</span>
                <span className="user-status">Online</span>
              </div>
            </div>
            <button onClick={handleLogout} className="taskifai-logout-btn">
              <span>Logout</span>
              <span className="logout-icon">→</span>
            </button>
          </div>
        </header>
      )}

      <div className="dashboard-main">
        {activeView === 'landing' ? (
          <LandingPage onNavigate={handleLandingNavigation} />
        ) : (
          <main className="taskifai-content">
            <div className="content-wrapper">
              {activeView === 'upload' ? (
                <Upload />
              ) : activeView === 'status' ? (
                <StatusList />
              ) : activeView === 'chat' ? (
                <ChatSection />
              ) : activeView === 'analytics' ? (
                <AnalyticsDashboard />
              ) : (
                <Upload />
              )}
            </div>
          </main>
        )}
      </div>

      <style jsx>{`
        .taskifai-dashboard {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          position: relative;
        }

        .taskifai-header {
          background: var(--surface-glass-strong);
          backdrop-filter: var(--glass-backdrop);
          color: var(--text-primary);
          padding: var(--space-6) var(--space-8);
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid var(--glass-border);
          box-shadow: var(--shadow-lg);
          gap: var(--space-8);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .header-left {
          display: flex;
          align-items: center;
        }

        .taskifai-brand {
          display: flex;
          align-items: center;
          gap: var(--space-4);
          transition: all var(--duration-150) var(--ease-out);
        }

        .taskifai-brand:hover {
          transform: scale(1.02);
        }

        .brand-icon {
          width: 48px;
          height: 48px;
          background: var(--gradient-primary);
          border-radius: var(--radius-xl);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-on-primary);
          font-size: var(--text-xl);
          font-weight: var(--font-extrabold);
          box-shadow: var(--shadow-md);
          border: 2px solid var(--glass-border);
        }

        .brand-text h1 {
          font-family: var(--font-display);
          font-size: var(--text-2xl);
          font-weight: var(--font-extrabold);
          background: var(--gradient-text);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin: 0;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          line-height: 1;
        }

        .brand-tagline {
          font-size: 0.875rem;
          color: var(--text-muted);
          font-weight: 400;
          opacity: 0.8;
        }

        .taskifai-nav {
          display: flex;
          gap: var(--space-2);
          align-items: center;
        }

        .nav-item {
          background: var(--surface-primary);
          color: var(--text-secondary);
          padding: var(--space-3) var(--space-4);
          border: 1px solid var(--border-light);
          border-radius: var(--radius-lg);
          font-weight: var(--font-medium);
          font-size: var(--text-sm);
          font-family: var(--font-sans);
          transition: all var(--duration-150) var(--ease-out);
          position: relative;
          overflow: hidden;
          white-space: nowrap;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: var(--space-2);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .nav-item:hover:not(.active) {
          background: var(--surface-secondary);
          color: var(--text-primary);
          transform: translateY(-1px);
          border-color: var(--border-medium);
          box-shadow: var(--shadow-sm);
        }

        .nav-item.active {
          background: var(--gradient-primary);
          color: var(--text-on-primary);
          box-shadow: var(--shadow-md);
          border-color: transparent;
        }

        .nav-icon {
          font-size: 1.125rem;
        }

        .nav-text {
          font-size: 0.9rem;
        }

        .header-user {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: var(--space-3);
        }

        .user-avatar {
          width: 40px;
          height: 40px;
          background: var(--gradient-primary);
          border-radius: var(--radius-lg);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-on-primary);
          font-size: var(--text-base);
          font-weight: var(--font-semibold);
          box-shadow: var(--shadow-sm);
          border: 1px solid var(--glass-border);
        }

        .user-details {
          display: flex;
          flex-direction: column;
          gap: var(--space-1);
        }

        .user-email {
          font-size: var(--text-sm);
          color: var(--text-primary);
          font-weight: var(--font-medium);
        }

        .user-status {
          font-size: var(--text-xs);
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.025em;
          font-weight: var(--font-medium);
        }

        .taskifai-logout-btn {
          padding: var(--space-2) var(--space-4);
          background-color: var(--surface-primary);
          color: var(--text-secondary);
          border: 1px solid var(--border-light);
          border-radius: var(--radius-lg);
          font-size: var(--text-xs);
          font-weight: var(--font-medium);
          cursor: pointer;
          transition: all var(--duration-150) var(--ease-out);
          display: flex;
          align-items: center;
          gap: var(--space-2);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .taskifai-logout-btn:hover {
          background-color: var(--surface-secondary);
          color: var(--text-primary);
          transform: translateY(-1px);
          box-shadow: var(--shadow-sm);
          border-color: var(--border-medium);
        }

        .logout-icon {
          font-size: 1rem;
          transition: transform 0.2s ease;
        }

        .taskifai-logout-btn:hover .logout-icon {
          transform: translateX(2px);
        }

        .dashboard-main {
          flex: 1;
          width: 100%;
          position: relative;
        }

        .taskifai-content {
          flex: 1;
          padding: var(--space-8);
          max-width: none;
          margin: 0;
          width: 100%;
          overflow-x: auto;
          background: var(--bibbi-background);
          position: relative;
          z-index: 1;
        }

        .taskifai-content::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(circle at 20% 30%, var(--primary-50) 0%, transparent 40%),
                      radial-gradient(circle at 80% 70%, var(--primary-100) 0%, transparent 40%);
          opacity: 0.4;
          pointer-events: none;
        }

        .content-wrapper {
          max-width: var(--max-width-7xl);
          margin: 0 auto;
          position: relative;
          z-index: 1;
        }


        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }

        @media (max-width: 1024px) {
          .taskifai-header {
            padding: 1rem 1.5rem;
          }

          .taskifai-nav {
            gap: 0.25rem;
          }

          .nav-item {
            padding: 0.625rem 0.875rem;
            font-size: 0.85rem;
          }

          .nav-text {
            display: none;
          }

          .nav-icon {
            font-size: 1.25rem;
          }
        }

        @media (max-width: 768px) {
          .taskifai-header {
            padding: 1rem;
            flex-wrap: wrap;
            gap: 1rem;
          }

          .header-left {
            order: 1;
            flex: 1;
          }

          .header-user {
            order: 2;
          }

          .taskifai-nav {
            order: 3;
            width: 100%;
            justify-content: center;
            overflow-x: auto;
            padding: 0.5rem 0;
          }

          .user-details {
            display: none;
          }

          .brand-text h1 {
            font-size: 1.5rem;
          }

          .brand-icon {
            width: 40px;
            height: 40px;
            font-size: 20px;
          }

          .taskifai-content {
            padding: 1rem;
          }
        }

        @media (max-width: 480px) {
          .taskifai-header {
            padding: 0.75rem;
          }

          .taskifai-nav {
            gap: 0.25rem;
          }

          .nav-item {
            padding: 0.5rem 0.75rem;
            min-width: max-content;
          }

          .brand-tagline {
            display: none;
          }

          .taskifai-content {
            padding: 0.75rem;
          }
        }
      `}</style>
    </div>
  )
}

export default Dashboard