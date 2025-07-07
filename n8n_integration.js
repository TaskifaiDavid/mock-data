// n8n RAG Integration for BIBBI Chat
// This replaces the current chat API call with the new n8n RAG system

class N8nRagService {
  constructor(n8nWebhookUrl) {
    this.webhookUrl = n8nWebhookUrl; // Your n8n webhook URL
    this.timeout = 30000; // 30 second timeout for complex queries
  }

  /**
   * Send a question to the n8n RAG system
   * @param {string} question - The user's question
   * @param {string} userId - User ID for data filtering
   * @param {string} sessionId - Session ID for conversation context
   * @returns {Promise<Object>} - Structured response from RAG system
   */
  async askQuestion(question, userId = null, sessionId = null) {
    try {
      console.log('🚀 Sending question to n8n RAG:', question);
      
      const requestPayload = {
        query: question,
        message: question, // Alternative field name
        userId: userId,
        sessionId: sessionId,
        timestamp: new Date().toISOString()
      };

      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
        timeout: this.timeout
      });

      if (!response.ok) {
        throw new Error(`n8n webhook returned ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('✅ n8n RAG response:', result);

      return this.formatResponse(result);

    } catch (error) {
      console.error('❌ n8n RAG error:', error);
      throw error;
    }
  }

  /**
   * Format the n8n response to match the expected chat interface format
   * @param {Object} rawResponse - Raw response from n8n
   * @returns {Object} - Formatted response for chat interface
   */
  formatResponse(rawResponse) {
    if (rawResponse.error || !rawResponse.success) {
      return {
        success: false,
        message: rawResponse.message || 'An error occurred processing your question.',
        error: rawResponse.details?.error || 'Unknown error',
        timestamp: rawResponse.details?.timestamp || new Date().toISOString()
      };
    }

    return {
      success: true,
      message: rawResponse.message,
      questionType: rawResponse.questionType,
      timestamp: rawResponse.timestamp,
      
      // Include data for potential table display
      results: this.extractTableData(rawResponse),
      resultsCount: this.getResultsCount(rawResponse),
      
      // Include summary for quick insights
      summary: rawResponse.data?.summary,
      
      // Metadata for debugging
      metadata: {
        originalQuestion: rawResponse.metadata?.originalQuestion,
        processingTime: rawResponse.metadata?.processingTime,
        dataPoints: rawResponse.metadata?.dataPoints
      }
    };
  }

  /**
   * Extract table data for display if needed
   * @param {Object} response - n8n response
   * @returns {Array} - Array of records for table display
   */
  extractTableData(response) {
    if (!response.data?.results) return null;

    const results = response.data.results;
    
    // Return the most relevant dataset for table display
    if (results.reseller_performance && Array.isArray(results.reseller_performance)) {
      return results.reseller_performance;
    } else if (results.product_performance && Array.isArray(results.product_performance)) {
      return results.product_performance;
    } else if (results.general_sales && Array.isArray(results.general_sales)) {
      return results.general_sales.slice(0, 10); // Limit for display
    } else if (results.time_series && Array.isArray(results.time_series)) {
      return results.time_series;
    }

    return null;
  }

  /**
   * Get the count of results
   * @param {Object} response - n8n response
   * @returns {number} - Number of results
   */
  getResultsCount(response) {
    const results = this.extractTableData(response);
    if (results && Array.isArray(results)) {
      return results.length;
    }
    
    // Check summary for record counts
    if (response.data?.summary?.totalRecords) {
      return response.data.summary.totalRecords;
    }
    if (response.data?.summary?.recordCount) {
      return response.data.summary.recordCount;
    }

    return 0;
  }

  /**
   * Test the connection to n8n webhook
   * @returns {Promise<boolean>} - True if connection successful
   */
  async testConnection() {
    try {
      const response = await this.askQuestion('Hello, are you working?', 'test-user', 'test-session');
      return response.success;
    } catch (error) {
      console.error('n8n connection test failed:', error);
      return false;
    }
  }
}

// Usage Examples:

// 1. Initialize the service
const ragService = new N8nRagService('https://your-n8n-instance.com/webhook/bibbi-chat');

// 2. Example questions and expected behavior:
async function testRagService() {
  const userId = 'user-123';
  const sessionId = 'session-456';

  try {
    // Direct answer questions
    let response = await ragService.askQuestion('What are my total sales?', userId, sessionId);
    console.log('Total sales:', response.message); // Should get direct answer like "Your total sales are €4,657.48"

    // Top performer questions  
    response = await ragService.askQuestion('Who is my top reseller?', userId, sessionId);
    console.log('Top reseller:', response.message); // Should get "Your top reseller is Liberty with €2,234.29"

    // List questions (should include table data)
    response = await ragService.askQuestion('Show me all my resellers', userId, sessionId);
    console.log('Resellers list:', response.message); // Should get summary + response.results for table
    console.log('Table data:', response.results); // Array of reseller data

    // Complex analysis
    response = await ragService.askQuestion('Analyze my sales performance by month for 2025', userId, sessionId);
    console.log('Analysis:', response.message); // Should get detailed analysis
    console.log('Data points:', response.metadata.dataPoints);

  } catch (error) {
    console.error('Test failed:', error);
  }
}

// 3. Integration with existing chat interface:
// Replace the existing sendChatQuery call with:
export async function sendChatQueryRAG(queryRequest) {
  const ragService = new N8nRagService(process.env.N8N_WEBHOOK_URL || 'https://your-n8n-instance.com/webhook/bibbi-chat');
  
  return await ragService.askQuestion(
    queryRequest.message,
    queryRequest.userId,
    queryRequest.sessionId
  );
}

// 4. Environment Configuration:
// Add to your .env file:
// N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/bibbi-chat
// N8N_TIMEOUT=30000

export default N8nRagService;