import React, { useState, useEffect, useRef } from 'react'
import { sendChatQuery, getChatHistory, clearChatSession } from '../services/api'
import DataVisualization from './DataVisualization'

const ChatInterface = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [showSqlQuery, setShowSqlQuery] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('checking')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Initialize with an enhanced welcome message with more examples
    setMessages([
      {
        type: 'assistant',
        content: `Hello! I'm your AI sales data assistant. I can help you with both normal conversations and sales data analysis.

**💬 Just Chat**: Feel free to say "Hi", ask how I work, or have a normal conversation!

**📊 Sales Data Questions**: Ask me about your business data in plain English:
• "What are my total sales this year?"
• "Show me my top 5 resellers"
• "Which products sold the most last month?"
• "How did Q4 perform compared to Q3?"

**🚀 I'm Smart**: I can tell the difference between casual chat and data questions, so feel free to interact naturally!

Try saying "Hi" or ask me a specific question about your sales data!`,
        timestamp: new Date().toISOString(),
        showSuggestions: true
      }
    ])
    
    // Check connection status on mount
    checkServerConnection().then(isConnected => {
      setConnectionStatus(isConnected ? 'connected' : 'disconnected')
    })
  }, [])

  const checkServerConnection = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/health`, {
        method: 'GET',
        timeout: 5000
      })
      return response.ok
    } catch (error) {
      console.error('Server connection check failed:', error)
      return false
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return

    // Check authentication
    const token = localStorage.getItem('access_token')
    if (!token) {
      setError('You need to log in to use the chat feature.')
      return
    }

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)
    setError(null)

    try {
      const response = await sendChatQuery({
        message: inputMessage,
        sessionId: sessionId
      })

      const assistantMessage = {
        type: 'assistant',
        content: response.message,
        timestamp: response.timestamp,
        sqlQuery: response.sqlQuery,
        results: response.results,
        resultsCount: response.resultsCount,
        success: response.success,
        showResults: response.results && response.results.length > 0,
        originalQuery: inputMessage // Store original user query for visualization context
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Set session ID if this is the first message
      if (!sessionId && response.sessionId) {
        setSessionId(response.sessionId)
      }

    } catch (err) {
      console.error('Error sending chat message:', err)
      console.error('Error type:', typeof err)
      console.error('Error constructor:', err?.constructor?.name)
      console.error('Error keys:', err ? Object.keys(err) : 'No error object')
      
      // Categorize the error type
      let errorType = 'unknown'
      let errorMessage = 'Unknown error occurred'
      let isNetworkError = false
      
      if (!err) {
        errorType = 'null_error'
        errorMessage = 'No error information available'
      } else if (err.name === 'TypeError' && err.message?.includes('fetch')) {
        errorType = 'network_error'
        errorMessage = 'Network connection failed. Please check if the server is running.'
        isNetworkError = true
      } else if (err.name === 'TypeError') {
        errorType = 'type_error'
        errorMessage = `Type error: ${err.message || 'Invalid operation'}`
      } else if (err.response) {
        // This is an HTTP response error (like 4xx, 5xx)
        errorType = 'http_error'
        const status = err.response.status || 'Unknown status'
        if (status === 401) {
          errorMessage = 'Authentication failed. Please log in again.'
        } else if (status === 403) {
          errorMessage = 'Access denied. Check your permissions.'
        } else if (status === 404) {
          errorMessage = 'API endpoint not found. Check server configuration.'
        } else if (status >= 500) {
          errorMessage = `Server error: ${status}. Please try again later.`
        } else {
          errorMessage = `Server error: ${status}`
        }
      } else if (err.message) {
        errorType = 'general_error'
        errorMessage = err.message
      } else {
        errorType = 'unknown_error'
        errorMessage = 'An unexpected error occurred'
      }
      
      // Show detailed error information in development
      const isDev = import.meta.env.DEV
      let errorContent = `I encountered an error: ${errorMessage}`
      
      if (isDev) {
        errorContent += `\n\nDebug Info:`
        errorContent += `\nError Type: ${errorType}`
        errorContent += `\nNetwork Error: ${isNetworkError}`
        
        if (err?.response?.data) {
          errorContent += `\nResponse Data: ${JSON.stringify(err.response.data, null, 2)}`
        }
        
        if (err?.message) {
          errorContent += `\nError Message: ${err.message}`
        }
        
        if (err?.stack) {
          errorContent += `\nStack Trace: ${err.stack.substring(0, 500)}...`
        }
      }
      
      // Set user-friendly error message
      setError(isNetworkError 
        ? 'Connection failed - please check if the server is running'
        : `Failed to send message: ${errorMessage}`
      )
      
      const errorMsg = {
        type: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString(),
        success: false,
        errorType: errorType,
        isNetworkError: isNetworkError,
        error: isDev ? err : undefined
      }
      
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleClearChat = async () => {
    if (!sessionId) {
      setMessages([])
      return
    }

    try {
      await clearChatSession(sessionId)
      setMessages([])
      setSessionId(null)
      setError(null)
    } catch (err) {
      console.error('Error clearing chat:', err)
      setError('Failed to clear chat session')
    }
  }

  // Remove old formatResults function - replaced with DataVisualization component

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion)
  }

  const MessageBubble = ({ message }) => (
    <div className={`message ${message.type}`}>
      <div className="message-content">
        {message.content.split('\n').map((line, index) => (
          <p key={index}>{line}</p>
        ))}
        
        {message.showSuggestions && (
          <div className="query-suggestions">
            <h4>Try These Examples:</h4>
            <div className="suggestion-buttons">
              <button 
                className="suggestion-btn conversation" 
                onClick={() => handleSuggestionClick("Hi")}
              >
                💬 Say Hi
              </button>
              <button 
                className="suggestion-btn conversation" 
                onClick={() => handleSuggestionClick("What can you do?")}
              >
                🤔 What Can You Do?
              </button>
              <button 
                className="suggestion-btn data" 
                onClick={() => handleSuggestionClick("What are my total sales this year?")}
              >
                📊 Total Sales This Year
              </button>
              <button 
                className="suggestion-btn data" 
                onClick={() => handleSuggestionClick("Show me my top 5 resellers")}
              >
                🏆 Top 5 Resellers
              </button>
              <button 
                className="suggestion-btn data" 
                onClick={() => handleSuggestionClick("Which products sold the most last month?")}
              >
                🛍️ Best Products Last Month
              </button>
              <button 
                className="suggestion-btn conversation" 
                onClick={() => handleSuggestionClick("How does this work?")}
              >
                ❓ How Does This Work?
              </button>
            </div>
          </div>
        )}
        
        {message.sqlQuery && showSqlQuery && (
          <div className="sql-query">
            <strong>SQL Query:</strong>
            <pre>{message.sqlQuery}</pre>
          </div>
        )}
        
        {showSqlQuery && message.error && (
          <div className="debug-info">
            <strong>Debug Information:</strong>
            <pre>{JSON.stringify(message.error, null, 2)}</pre>
          </div>
        )}
        
        {showSqlQuery && message.resultsCount !== undefined && (
          <div className="debug-info">
            <strong>Results Count:</strong> {message.resultsCount}
          </div>
        )}
        
        {message.showResults && message.results && (
          <DataVisualization 
            results={message.results} 
            sqlQuery={message.sqlQuery}
            originalMessage={message.originalQuery || ''} 
          />
        )}
      </div>
      <div className="message-time">
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
    </div>
  )

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-title-section">
          <h2>Chat</h2>
          <div className="status-indicators">
            <div className={`connection-status ${connectionStatus}`}>
              <span className="status-dot"></span>
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
            </div>
            {localStorage.getItem('access_token') ? (
              <div className="auth-status authenticated">
                <span className="status-dot"></span>
                Authenticated
              </div>
            ) : (
              <div className="auth-status not-authenticated">
                <span className="status-dot"></span>
                Not logged in
              </div>
            )}
          </div>
        </div>
        <div className="chat-controls">
          <label className="sql-toggle">
            <input
              type="checkbox"
              checked={showSqlQuery}
              onChange={(e) => setShowSqlQuery(e.target.checked)}
            />
            Show SQL Queries
          </label>
          <button onClick={handleClearChat} className="clear-btn">
            Clear Chat
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        
        {loading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about your sales data..."
            disabled={loading}
            rows={1}
          />
          <button 
            onClick={handleSendMessage}
            disabled={loading || !inputMessage.trim()}
            className="send-btn"
          >
            {loading ? '...' : '→'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface