import React, { useState } from 'react'
import Upload from '../components/Upload'
import StatusList from '../components/StatusList'
import AnalyticsDashboard from '../components/AnalyticsDashboard'
import ChatSection from '../components/ChatSection'
import LandingPage from '../components/LandingPage'

function Dashboard({ user, onLogout }) {
  const [activeView, setActiveView] = useState('landing')

  console.log('Dashboard rendered with user:', user)

  const handleLogout = () => {
    console.log('Logout clicked')
    if (onLogout) {
      onLogout()
    }
  }

  const handleLandingNavigation = (view) => {
    setActiveView(view)
  }

  return (
    <div className="dashboard">
      {activeView !== 'landing' && (
        <header className="dashboard-header">
          <div className="header-left">
            <h1 
              onClick={() => setActiveView('landing')}
              style={{ cursor: 'pointer' }}
            >
              TaskifAI
            </h1>
          </div>
          
          <nav className="header-nav">
            <button
              className={activeView === 'upload' ? 'active' : ''}
              onClick={() => setActiveView('upload')}
            >
              📁 Upload Files
            </button>
            <button
              className={activeView === 'status' ? 'active' : ''}
              onClick={() => setActiveView('status')}
            >
              ⏱️ Processing Status
            </button>
            <button
              className={activeView === 'chat' ? 'active' : ''}
              onClick={() => setActiveView('chat')}
            >
              💬 Chat
            </button>
            <button
              className={activeView === 'analytics' ? 'active' : ''}
              onClick={() => setActiveView('analytics')}
            >
              📊 Analytics
            </button>
          </nav>

          <div className="user-info">
            <span>{user?.email || 'Unknown User'}</span>
            <button onClick={handleLogout} className="logout-btn btn-secondary">
              Logout
            </button>
          </div>
        </header>
      )}

      <div className="dashboard-main">
        {activeView === 'landing' ? (
          <LandingPage onNavigate={handleLandingNavigation} />
        ) : (
          <main className="dashboard-content">
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
          </main>
        )}
      </div>
      
      {/* Background Decorative Elements */}
      <div className="bg-decorations">
        <div className="floating-shape shape-1"></div>
        <div className="floating-shape shape-2"></div>
        <div className="floating-shape shape-3"></div>
        <div className="floating-shape shape-4"></div>
      </div>
    </div>
  )
}

export default Dashboard