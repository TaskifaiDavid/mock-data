import React, { useState } from 'react'
import { supabase } from '../services/supabase'
import Upload from '../components/Upload'
import StatusList from '../components/StatusList'

function Dashboard({ session }) {
  const [activeView, setActiveView] = useState('upload')

  const handleLogout = async () => {
    await supabase.auth.signOut()
    localStorage.removeItem('access_token')
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Data Cleaning Pipeline</h1>
        <div className="user-info">
          <span>{session.user.email}</span>
          <button onClick={handleLogout} className="logout-btn">
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