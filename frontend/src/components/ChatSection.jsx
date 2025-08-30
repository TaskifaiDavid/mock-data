import React, { useState, useRef, useEffect } from 'react'
import { renderMathContent } from '../utils/mathRenderer'

const ChatSection = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const currentMessage = inputMessage.trim() // Store current message
    const userMessage = { type: 'user', content: currentMessage, timestamp: new Date() }
    
    // Update state immediately
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('No authentication token found. Please login again.')
      }

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: currentMessage }) // Use stored message
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.')
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      const aiMessage = { type: 'ai', content: data.answer, timestamp: new Date() }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Chat request failed:', error.message)
      const errorMessage = { 
        type: 'ai', 
        content: `Error: ${error.message || 'Unable to process your question. Please try again.'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content)
  }

  const sampleQuestions = [
    "What were our total sales in 2024?",
    "Which reseller has the highest revenue?",
    "Show me monthly sales trends",
    "What are our top-selling products?",
    "Compare Q1 vs Q2 performance",
    "Which months had the best sales?"
  ]

  return (
    <div className="chat-section">
      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="welcome-section">
              <div className="welcome-message">
                <h3>👋 Welcome to Chat!</h3>
                <p>I can help you analyze your sales data. Here are some questions you can ask:</p>
              </div>
              
              <div className="sample-questions">
                <h4>Sample Questions:</h4>
                <div className="question-grid">
                  {sampleQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="sample-question"
                      onClick={() => setInputMessage(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-header">
                <span className="message-sender">
                  {message.type === 'user' ? '👤 You' : '🤖 AI Assistant'}
                </span>
                <span className="message-time">
                  {message.timestamp?.toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                <div className="math-content">{renderMathContent(message.content)}</div>
                {message.type === 'ai' && (
                  <button 
                    className="copy-btn"
                    onClick={() => copyMessage(message.content)}
                    title="Copy response"
                  >
                    📋
                  </button>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message ai">
              <div className="message-header">
                <span className="message-sender">🤖 AI Assistant</span>
                <span className="message-time">Analyzing...</span>
              </div>
              <div className="message-content">
                <pre>Analyzing your data<span className="loading-dots"><span>.</span><span>.</span><span>.</span></span></pre>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-section">
          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask a question about your sales data... (Press Enter to send, Shift+Enter for new line)"
              disabled={isLoading}
              rows={3}
              className="chat-input"
              autoFocus={false}
            />
            <button 
              onClick={sendMessage} 
              disabled={isLoading || !inputMessage.trim()}
              className="send-btn"
            >
              {isLoading ? '⏳' : '📤'} Send
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .chat-section {
          display: flex;
          flex-direction: column;
          height: calc(85vh - 102px + 8.5vh);
          background: var(--surface-primary);
          border-radius: var(--radius-lg);
          overflow: hidden;
          width: 80%;
          margin: 0 auto;
          border: 1px solid var(--border-light);
          box-shadow: var(--shadow-md);
        }

        .chat-container {
          display: flex;
          flex-direction: column;
          flex: 1;
          background: var(--surface-primary);
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          max-height: calc(85vh - 238px + 8.5vh);
          padding: var(--spacing-lg);
          background: var(--surface-secondary);
          scroll-behavior: smooth;
        }

        .welcome-section {
          text-align: center;
          max-width: 800px;
          margin: var(--spacing-2xl) auto;
        }

        .welcome-message {
          background: var(--surface-primary);
          padding: var(--spacing-2xl);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-sm);
          margin-bottom: var(--spacing-xl);
          border: 1px solid var(--border-light);
        }

        .welcome-message h3 {
          margin: 0 0 var(--spacing-md) 0;
          color: var(--text-primary);
          font-size: 1.5rem;
          font-weight: 600;
        }

        .welcome-message p {
          margin: 0;
          color: var(--text-secondary);
          font-size: 1rem;
          line-height: 1.5;
        }

        .sample-questions {
          background: var(--surface-primary);
          padding: var(--spacing-xl);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-sm);
          border: 1px solid var(--border-light);
        }

        .sample-questions h4 {
          margin: 0 0 var(--spacing-lg) 0;
          color: var(--text-primary);
          font-size: 1.125rem;
          font-weight: 600;
        }

        .question-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: var(--spacing-sm);
        }

        .sample-question {
          background: var(--surface-secondary);
          border: 1px solid var(--border-light);
          padding: var(--spacing-sm) var(--spacing-md);
          border-radius: var(--radius-md);
          cursor: pointer;
          text-align: left;
          font-size: 0.875rem;
          transition: all 0.2s ease;
          color: var(--text-primary);
        }

        .sample-question:hover {
          background: var(--surface-primary);
          border-color: var(--border-medium);
          transform: translateY(-1px);
          box-shadow: var(--shadow-sm);
        }

        .message {
          margin-bottom: var(--spacing-lg);
          max-width: 85%;
        }

        .message.user {
          margin-left: auto;
        }

        .message.ai {
          margin-right: auto;
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-xs);
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .message-sender {
          font-weight: 600;
        }

        .message-time {
          opacity: 0.7;
        }

        .message-content {
          position: relative;
          padding: var(--spacing-md) var(--spacing-lg);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-sm);
          word-wrap: break-word;
          overflow-wrap: break-word;
          max-width: 100%;
        }

        .message.user .message-content {
          background: var(--notion-black);
          color: var(--notion-white);
          border-bottom-right-radius: var(--radius-sm);
        }

        .message.ai .message-content {
          background: var(--surface-primary);
          color: var(--text-primary);
          border: 1px solid var(--border-light);
          border-bottom-left-radius: var(--radius-sm);
        }

        .message-content pre {
          margin: 0;
          white-space: pre-wrap;
          word-wrap: break-word;
          overflow-wrap: break-word;
          font-family: inherit;
          font-size: 0.875rem;
          line-height: 1.5;
          max-width: 100%;
          overflow-x: auto;
        }

        .copy-btn {
          position: absolute;
          top: var(--spacing-xs);
          right: var(--spacing-xs);
          background: var(--surface-secondary);
          border: 1px solid var(--border-light);
          border-radius: var(--radius-sm);
          padding: 2px var(--spacing-xs);
          cursor: pointer;
          font-size: 0.6rem;
          opacity: 0.7;
          transition: opacity 0.2s ease;
          color: var(--text-secondary);
        }

        .copy-btn:hover {
          opacity: 1;
          background: var(--surface-primary);
        }

        .loading-animation {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
          color: var(--text-muted);
        }

        .loading-dots {
          display: flex;
          gap: 2px;
        }

        .loading-dots span {
          animation: loading 1.4s infinite ease-in-out;
        }

        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes loading {
          0%, 80%, 100% { opacity: 0; }
          40% { opacity: 1; }
        }

        .chat-input-section {
          background: var(--surface-primary);
          border-top: 1px solid var(--border-light);
          padding: var(--spacing-lg);
        }

        .input-container {
          display: flex;
          gap: var(--spacing-sm);
          max-width: 1000px;
          margin: 0 auto;
        }

        .chat-input {
          flex: 1;
          border: 1px solid var(--border-medium);
          border-radius: var(--radius-md);
          padding: var(--spacing-sm) var(--spacing-md);
          resize: none;
          font-family: inherit;
          font-size: 0.875rem;
          line-height: 1.4;
          transition: border-color 0.2s ease;
          background: var(--surface-primary);
          color: var(--text-primary);
        }

        .chat-input:focus {
          outline: none;
          border-color: var(--border-focus);
          box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
        }

        .chat-input:disabled {
          background: var(--surface-secondary);
          cursor: not-allowed;
          color: var(--text-muted);
        }

        .send-btn {
          background: var(--notion-black);
          color: var(--notion-white);
          border: none;
          border-radius: var(--radius-md);
          padding: var(--spacing-sm) var(--spacing-xl);
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.2s ease;
          white-space: nowrap;
          min-width: 120px;
        }

        .send-btn:disabled {
          background: var(--neutral-400);
          cursor: not-allowed;
        }

        .send-btn:not(:disabled):hover {
          background: var(--neutral-800);
          transform: translateY(-1px);
          box-shadow: var(--shadow-sm);
        }

        @media (max-width: 1024px) {
          .chat-section {
            width: 90%;
          }
        }

        @media (max-width: 768px) {
          .chat-section {
            width: 95%;
          }

          .question-grid {
            grid-template-columns: 1fr;
          }

          .message {
            max-width: 95%;
          }

          .input-container {
            flex-direction: column;
          }

          .send-btn {
            align-self: flex-end;
          }
        }
      `}</style>
    </div>
  )
}

export default ChatSection