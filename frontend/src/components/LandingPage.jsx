import React from 'react'

const LandingPage = ({ onNavigate }) => {
  const navigationOptions = [
    {
      id: 'upload',
      title: '📁 Upload Files',
      description: 'Upload and process your data files',
      icon: '📁'
    },
    {
      id: 'status',
      title: '⏱️ Processing Status',
      description: 'View the status of your uploads',
      icon: '⏱️'
    },
    {
      id: 'analytics',
      title: '📊 Analytics',
      description: 'View data insights and analytics',
      icon: '📊'
    },
    {
      id: 'chat',
      title: '💬 Chat',
      description: 'Ask questions about your data',
      icon: '💬'
    }
  ]

  return (
    <div className="landing-page">
      <div className="landing-container">
        <div className="welcome-section">
          <h1 className="welcome-title">Welcome! What do you want to do today?</h1>
        </div>
        
        <div className="navigation-grid">
          {navigationOptions.map((option) => (
            <button
              key={option.id}
              className="nav-button"
              onClick={() => onNavigate(option.id)}
            >
              <div className="nav-icon">{option.icon}</div>
              <div className="nav-content">
                <h3 className="nav-title">{option.title}</h3>
                <p className="nav-description">{option.description}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      <style jsx>{`
        .landing-page {
          min-height: 100vh;
          width: 100vw;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
          background-size: 400% 400%;
          animation: gradientShift 15s ease infinite;
          padding: 2rem;
          margin: 0;
          box-sizing: border-box;
        }

        @keyframes gradientShift {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }

        .landing-container {
          max-width: 1000px;
          width: 100%;
          text-align: center;
        }

        .welcome-section {
          margin-bottom: 4rem;
        }

        .welcome-title {
          font-size: 3rem;
          font-weight: 600;
          color: white;
          margin: 0;
          text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          letter-spacing: 0.02em;
        }

        .navigation-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 2rem;
          max-width: 800px;
          margin: 0 auto;
        }

        .nav-button {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 24px;
          padding: 2.5rem;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
          min-height: 200px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .nav-button:hover {
          transform: translateY(-8px) scale(1.02);
          box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
          background: rgba(255, 255, 255, 1);
        }

        .nav-icon {
          font-size: 3rem;
          margin-bottom: 0.5rem;
        }

        .nav-content {
          text-align: center;
        }

        .nav-title {
          font-size: 1.5rem;
          font-weight: 600;
          color: #333;
          margin: 0 0 0.5rem 0;
          letter-spacing: 0.02em;
        }

        .nav-description {
          font-size: 1rem;
          color: #666;
          margin: 0;
          line-height: 1.5;
        }

        @media (max-width: 768px) {
          .welcome-title {
            font-size: 2rem;
          }

          .navigation-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
          }

          .nav-button {
            padding: 2rem;
            min-height: 160px;
          }

          .nav-icon {
            font-size: 2.5rem;
          }

          .nav-title {
            font-size: 1.25rem;
          }
        }

        @media (max-width: 480px) {
          .landing-page {
            padding: 1rem;
          }

          .welcome-title {
            font-size: 1.5rem;
          }

          .nav-button {
            padding: 1.5rem;
            min-height: 140px;
          }
        }
      `}</style>
    </div>
  )
}

export default LandingPage