import React, { useState, useEffect } from 'react'
import { generateReport, sendReportEmail, getEmailLogs } from '../services/api'

const EmailReporting = () => {
  const [reports, setReports] = useState([])
  const [emailLogs, setEmailLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  // Form state
  const [reportForm, setReportForm] = useState({
    format: 'pdf',
    recipientEmail: 'report@bibbi-parfum.com',
    autoSend: false,
    uploadId: null
  })

  useEffect(() => {
    fetchEmailLogs()
  }, [])

  const fetchEmailLogs = async () => {
    try {
      const response = await getEmailLogs()
      setEmailLogs(response.logs || [])
    } catch (err) {
      console.error('Failed to fetch email logs:', err.message)
      setError('Failed to load email logs')
    }
  }

  const handleGenerateReport = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      const response = await generateReport(reportForm)
      
      if (reportForm.autoSend && response.email) {
        setSuccess(`Report generated and sent to ${reportForm.recipientEmail}`)
        fetchEmailLogs() // Refresh logs
      } else {
        setSuccess('Report generated successfully')
        // Trigger download
        const link = document.createElement('a')
        link.href = `data:${response.report.content_type};base64,${response.report.data}`
        link.download = response.report.filename
        link.click()
      }
    } catch (err) {
      console.error('Failed to generate report:', err.message)
      setError('Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setReportForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="email-reporting">
      <h2>Email Reporting</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {success && (
        <div className="success-message">
          {success}
        </div>
      )}
      
      <div className="report-generation">
        <h3>Generate Report</h3>
        
        <div className="form-group">
          <label>Format:</label>
          <select 
            name="format" 
            value={reportForm.format}
            onChange={handleInputChange}
          >
            <option value="pdf">PDF</option>
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Recipient Email:</label>
          <input
            type="email"
            name="recipientEmail"
            value={reportForm.recipientEmail}
            onChange={handleInputChange}
            placeholder="Enter recipient email"
          />
        </div>
        
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              name="autoSend"
              checked={reportForm.autoSend}
              onChange={handleInputChange}
            />
            Auto-send via email
          </label>
        </div>
        
        <button 
          onClick={handleGenerateReport}
          disabled={loading}
          className="generate-btn"
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>
      
      <div className="email-logs">
        <h3>Email History</h3>
        
        {emailLogs.length === 0 ? (
          <p>No email logs found.</p>
        ) : (
          <div className="logs-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Recipient</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {emailLogs.map((log) => (
                  <tr key={log.id}>
                    <td>{formatDate(log.sent_at)}</td>
                    <td>{log.recipient_email}</td>
                    <td>{log.email_type}</td>
                    <td>
                      <span className={`status ${log.status}`}>
                        {log.status}
                      </span>
                    </td>
                    <td>
                      {log.metadata && (
                        <div className="metadata">
                          {log.metadata.cleanedRows && (
                            <span>Rows: {log.metadata.cleanedRows}</span>
                          )}
                          {log.metadata.totalValue && (
                            <span>Value: {log.metadata.totalValue} EUR</span>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default EmailReporting