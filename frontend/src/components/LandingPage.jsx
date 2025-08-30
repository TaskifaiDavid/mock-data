import React from 'react'

const LandingPage = ({ onNavigate }) => {
  const navigationOptions = [
    {
      id: 'upload',
      title: 'Upload Data',
      description: 'Transform chaotic data files into structured insights',
      icon: '📊',
      color: 'from-taskifai-blue-500 to-taskifai-blue-600'
    },
    {
      id: 'status',
      title: 'Processing Status',
      description: 'Track your data transformation progress',
      icon: '⚡',
      color: 'from-taskifai-blue-400 to-taskifai-blue-500'
    },
    {
      id: 'analytics',
      title: 'Analytics',
      description: 'Discover patterns and insights instantly',
      icon: '🔍',
      color: 'from-taskifai-blue-600 to-taskifai-blue-700'
    },
    {
      id: 'chat',
      title: 'AI Assistant',
      description: 'Get instant answers about your data',
      icon: '🤖',
      color: 'from-taskifai-blue-500 to-taskifai-blue-700'
    }
  ]

  return (
    <div className="taskifai-landing">
      <div className="landing-container">
        {/* TaskifAI Header */}
        <div className="taskifai-header">
          <div className="taskifai-logo">
            <div className="logo-icon">T</div>
            <span className="logo-text">TaskifAI</span>
          </div>
        </div>
        
        {/* Navigation Cards */}
        <div className="taskifai-grid">
          {navigationOptions.map((option) => (
            <button
              key={option.id}
              className="taskifai-card"
              onClick={() => onNavigate(option.id)}
            >
              <div className="card-icon">{option.icon}</div>
              <div className="card-content">
                <h3 className="card-title">{option.title}</h3>
                <p className="card-description">{option.description}</p>
              </div>
              <div className="card-arrow">→</div>
            </button>
          ))}
        </div>
        
        {/* Features Preview */}
        <div className="features-preview">
          <div className="feature-item">
            <span className="feature-icon">🚀</span>
            <span className="feature-text">AI-powered insights</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚡</span>
            <span className="feature-text">Instant processing</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔐</span>
            <span className="feature-text">Secure & compliant</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .taskifai-landing {
          min-height: 100vh;
          width: 100vw;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bibbi-background);
          position: relative;
          overflow: hidden;
          margin: 0;
          padding: var(--space-8);
        }

        .taskifai-landing::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(circle at 30% 20%, var(--primary-50) 0%, transparent 50%),
                      radial-gradient(circle at 70% 80%, var(--primary-100) 0%, transparent 50%);
          opacity: 0.6;
          pointer-events: none;
        }

        .landing-container {
          width: 100%;
          text-align: center;
          position: relative;
          z-index: 1;
          max-width: var(--max-width-6xl);
          margin: 0 auto;
          padding: var(--space-12);
        }

        .taskifai-header {
          margin-bottom: var(--space-20);
        }

        .taskifai-logo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--space-4);
          margin-bottom: var(--space-16);
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
          font-size: var(--text-5xl);
          font-weight: var(--font-extrabold);
          background: var(--gradient-text);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }


        .taskifai-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--space-8);
          max-width: var(--max-width-4xl);
          margin: 0 auto var(--space-20) auto;
        }

        .taskifai-card {
          background: var(--surface-glass);
          backdrop-filter: var(--glass-backdrop);
          border: 1px solid var(--glass-border);
          border-radius: var(--radius-2xl);
          padding: var(--space-8);
          cursor: pointer;
          transition: all var(--duration-200) var(--ease-out);
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          text-align: left;
          position: relative;
          overflow: hidden;
          min-height: 180px;
          box-shadow: var(--shadow-lg);
        }

        .taskifai-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: var(--gradient-primary);
          opacity: 0;
          transition: opacity var(--duration-200) var(--ease-out);
        }

        .taskifai-card:hover {
          transform: translateY(-4px);
          box-shadow: var(--shadow-xl);
          border-color: var(--primary-200);
        }

        .taskifai-card:hover::before {
          opacity: 1;
        }

        .card-icon {
          font-size: var(--text-4xl);
          margin-bottom: var(--space-6);
          opacity: 0.9;
          filter: grayscale(0.2);
        }

        .card-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: var(--space-3);
        }

        .card-title {
          font-family: var(--font-display);
          font-size: var(--text-xl);
          font-weight: var(--font-bold);
          color: var(--text-primary);
          margin: 0;
          line-height: var(--leading-tight);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .card-description {
          font-size: var(--text-sm);
          color: var(--text-secondary);
          margin: 0;
          line-height: var(--leading-relaxed);
          font-weight: var(--font-normal);
        }

        .card-arrow {
          position: absolute;
          top: var(--space-8);
          right: var(--space-8);
          font-size: var(--text-xl);
          color: var(--primary-400);
          opacity: 0;
          transform: translateX(-8px);
          transition: all var(--duration-200) var(--ease-out);
          font-weight: var(--font-bold);
        }

        .taskifai-card:hover .card-arrow {
          opacity: 1;
          transform: translateX(0);
          color: var(--primary-600);
        }

        .features-preview {
          display: flex;
          justify-content: center;
          gap: var(--space-12);
          margin-top: var(--space-16);
        }

        .feature-item {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          color: var(--text-secondary);
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .feature-icon {
          font-size: var(--text-lg);
          opacity: 0.9;
        }

        .feature-text {
          opacity: 0.9;
        }

        @media (max-width: 768px) {
          .taskifai-grid {
            grid-template-columns: 1fr;
            gap: var(--spacing-lg);
          }

          .taskifai-card {
            padding: var(--spacing-lg);
            min-height: 136px;
          }

          .card-title {
            font-size: 1.06rem;
          }

          .card-description {
            font-size: 0.8rem;
          }

          .features-preview {
            flex-direction: column;
            gap: var(--spacing-md);
            align-items: center;
          }

          .logo-text {
            font-size: 1.7rem;
          }

          .logo-icon {
            width: 42px;
            height: 42px;
            font-size: 1.5rem;
          }
        }

        @media (max-width: 480px) {
          .landing-container {
            padding: var(--spacing-md);
          }

          .taskifai-card {
            padding: var(--spacing-md);
            min-height: 119px;
          }

          .card-icon {
            font-size: 1.7rem;
          }

          .card-title {
            font-size: 0.96rem;
          }
        }
      `}</style>
    </div>
  )
}

export default LandingPage