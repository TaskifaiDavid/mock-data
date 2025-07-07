import React, { useState } from 'react'
import Upload from '../components/Upload'
import StatusList from '../components/StatusList'
import ChatInterface from '../components/ChatInterface'
import AnalyticsDashboard from '../components/AnalyticsDashboard'

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
        <h1>BIBBI</h1>
        <div className="user-info">
          <span>{user?.email || 'Unknown User'}</span>
          <button onClick={handleLogout} className="logout-btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-main">
        <nav className="dashboard-nav">
          <button
            className={activeView === 'upload' ? 'active' : ''}
            onClick={() => setActiveView('upload')}
          >
            Upload Files
          </button>
          <button
            className={activeView === 'status' ? 'active' : ''}
            onClick={() => setActiveView('status')}
          >
            Processing Status
          </button>
          <button
            className={activeView === 'chat' ? 'active' : ''}
            onClick={() => setActiveView('chat')}
          >
            Chat
          </button>
          <button
            className={activeView === 'analytics' ? 'active' : ''}
            onClick={() => setActiveView('analytics')}
          >
            Analytics
          </button>
        </nav>

        <main className="dashboard-content">
        {activeView === 'upload' ? (
          <Upload />
        ) : activeView === 'status' ? (
          <StatusList />
        ) : activeView === 'chat' ? (
          <ChatInterface />
        ) : (
          <AnalyticsDashboard />
        )}
        </main>
      </div>
    </div>
  )
}

export default Dashboard