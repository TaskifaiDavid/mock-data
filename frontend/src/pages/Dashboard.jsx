import React, { useState } from 'react'
import Upload from '../components/Upload'
import StatusList from '../components/StatusList'
import AnalyticsDashboard from '../components/AnalyticsDashboard'
import ChatSection from '../components/ChatSection'

function Dashboard({ user, onLogout }) {
  const [activeView, setActiveView] = useState('upload')

  console.log('Dashboard rendered with user:', user)

  const handleLogout = () => {
    console.log('Logout clicked')
    if (onLogout) {
      onLogout()
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>TaskifAI</h1>
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
            className={activeView === 'analytics' ? 'active' : ''}
            onClick={() => setActiveView('analytics')}
          >
            📊 Analytics
          </button>
          <button
            className={activeView === 'chat' ? 'active' : ''}
            onClick={() => setActiveView('chat')}
          >
            💬 Chat
          </button>
        </nav>

        <div className="user-info">
          <span>{user?.email || 'Unknown User'}</span>
          <button onClick={handleLogout} className="logout-btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-main">
        <main className="dashboard-content">
          {activeView === 'upload' ? (
            <Upload />
          ) : activeView === 'status' ? (
            <StatusList />
          ) : activeView === 'analytics' ? (
            <AnalyticsDashboard />
          ) : activeView === 'chat' ? (
            <ChatSection />
          ) : (
            <Upload />
          )}
        </main>
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