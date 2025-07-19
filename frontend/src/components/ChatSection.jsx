import React, { useState, useRef, useEffect } from 'react'

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
      console.error('Chat error:', error)
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

  const clearChat = () => {
    setMessages([])
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
      <div className="chat-header">
        <div className="header-content">
          <h2>💬 Data Chat</h2>
          <p>Ask questions about your sales data and get AI-powered insights</p>
        </div>
        <div className="chat-actions">
          <button onClick={clearChat} className="btn-secondary" disabled={messages.length === 0}>
            Clear Chat
          </button>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="welcome-section">
              <div className="welcome-message">
                <h3>👋 Welcome to Data Chat!</h3>
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
                <pre>{message.content}</pre>
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
              <div className="message-content loading">
                <div className="loading-animation">
                  <span>Analyzing your data</span>
                  <div className="loading-dots">
                    <span>.</span><span>.</span><span>.</span>
                  </div>
                </div>
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
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your sales data... (Press Enter to send, Shift+Enter for new line)"
              disabled={isLoading}
              rows={3}
              className="chat-input"
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
          height: calc(100vh - 120px);
          background: #f8f9fa;
          border-radius: 8px;
          overflow: hidden;
        }

        .chat-header {
          background: linear-gradient(135deg, #007bff, #0056b3);
          color: white;
          padding: 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-content h2 {
          margin: 0 0 5px 0;
          font-size: 24px;
        }

        .header-content p {
          margin: 0;
          opacity: 0.9;
          font-size: 14px;
        }

        .chat-actions .btn-secondary {
          background: rgba(255,255,255,0.2);
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        }

        .chat-actions .btn-secondary:hover:not(:disabled) {
          background: rgba(255,255,255,0.3);
        }

        .chat-actions .btn-secondary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .chat-container {
          display: flex;
          flex-direction: column;
          flex: 1;
          background: white;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          max-height: calc(100vh - 280px);
          padding: 20px;
          background: #fafafa;
          scroll-behavior: smooth;
        }

        .welcome-section {
          text-align: center;
          max-width: 800px;
          margin: 40px auto;
        }

        .welcome-message {
          background: white;
          padding: 30px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          margin-bottom: 30px;
        }

        .welcome-message h3 {
          margin: 0 0 15px 0;
          color: #333;
          font-size: 24px;
        }

        .welcome-message p {
          margin: 0;
          color: #666;
          font-size: 16px;
          line-height: 1.5;
        }

        .sample-questions {
          background: white;
          padding: 25px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .sample-questions h4 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 18px;
        }

        .question-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 12px;
        }

        .sample-question {
          background: #f8f9fa;
          border: 2px solid #e9ecef;
          padding: 12px 16px;
          border-radius: 8px;
          cursor: pointer;
          text-align: left;
          font-size: 14px;
          transition: all 0.2s ease;
        }

        .sample-question:hover {
          background: #e3f2fd;
          border-color: #007bff;
          transform: translateY(-1px);
        }

        .message {
          margin-bottom: 20px;
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
          margin-bottom: 8px;
          font-size: 12px;
          color: #666;
        }

        .message-sender {
          font-weight: 600;
        }

        .message-time {
          opacity: 0.7;
        }

        .message-content {
          position: relative;
          padding: 16px 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          word-wrap: break-word;
          overflow-wrap: break-word;
          max-width: 100%;
        }

        .message.user .message-content {
          background: #007bff;
          color: white;
          border-bottom-right-radius: 4px;
        }

        .message.ai .message-content {
          background: white;
          color: #333;
          border: 1px solid #e9ecef;
          border-bottom-left-radius: 4px;
        }

        .message-content pre {
          margin: 0;
          white-space: pre-wrap;
          word-wrap: break-word;
          overflow-wrap: break-word;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.5;
          max-width: 100%;
          overflow-x: auto;
        }

        .copy-btn {
          position: absolute;
          top: 8px;
          right: 8px;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 4px 8px;
          cursor: pointer;
          font-size: 12px;
          opacity: 0.7;
          transition: opacity 0.2s ease;
        }

        .copy-btn:hover {
          opacity: 1;
        }

        .loading-animation {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #666;
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
          background: white;
          border-top: 1px solid #e9ecef;
          padding: 20px;
        }

        .input-container {
          display: flex;
          gap: 12px;
          max-width: 1000px;
          margin: 0 auto;
        }

        .chat-input {
          flex: 1;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          padding: 12px 16px;
          resize: none;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.4;
          transition: border-color 0.2s ease;
        }

        .chat-input:focus {
          outline: none;
          border-color: #007bff;
        }

        .chat-input:disabled {
          background: #f8f9fa;
          cursor: not-allowed;
        }

        .send-btn {
          background: #007bff;
          color: white;
          border: none;
          border-radius: 8px;
          padding: 12px 24px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          transition: background-color 0.2s ease;
          white-space: nowrap;
        }

        .send-btn:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .send-btn:not(:disabled):hover {
          background: #0056b3;
        }

        @media (max-width: 768px) {
          .chat-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 15px;
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