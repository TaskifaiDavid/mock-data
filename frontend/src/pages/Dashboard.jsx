import React, { useState } from 'react'
import Upload from '../components/Upload'
import StatusList from '../components/StatusList'

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
        <h1>Data Pipeline</h1>
        <div className="user-info">
          <span>{user?.email || 'Unknown User'}</span>
          <button onClick={handleLogout} className="logout-btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button
          className={activeView === 'upload' ? 'active' : ''}
          onClick={() => setActiveView('upload')}
        >
          Upload File
        </button>
        <button
          className={activeView === 'status' ? 'active' : ''}
          onClick={() => setActiveView('status')}
        >
          Processing Status
        </button>
      </nav>

      <main className="dashboard-content">
        {activeView === 'upload' ? (
          <Upload />
        ) : (
          <StatusList />
        )}
      </main>
    </div>
  )
}

export default Dashboard