# BIBBI n8n RAG System Setup Guide

This guide will help you set up the advanced RAG (Retrieval-Augmented Generation) system using n8n for your BIBBI chat interface.

## Overview

The n8n RAG system provides:
- ✅ **Intelligent question processing** - Understands business context
- ✅ **Multi-table data retrieval** - Accesses all your Supabase tables
- ✅ **Advanced AI responses** - Uses GPT-4 with business context
- ✅ **Conversation memory** - Maintains context across questions
- ✅ **Error handling** - Graceful fallbacks and debugging

## Step 1: n8n Setup

### 1.1 Install n8n
```bash
npm install -g n8n
# OR use Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### 1.2 Import the Workflow
1. Open n8n at `http://localhost:5678`
2. Go to **Workflows** → **Import from file**
3. Upload the `bibbi_rag_workflow.json` file
4. The workflow will be imported with all nodes connected

## Step 2: Configure Credentials

### 2.1 Supabase Credentials
1. In n8n, go to **Credentials** → **Add Credential** → **Supabase**
2. Enter your Supabase details:
   ```
   Name: BIBBI Supabase
   Host: https://edckqdrbgtnnjfnshjfq.supabase.co
   Service Role Key: [Your Supabase Service Key from .env]
   ```

### 2.2 OpenAI Credentials
1. Add **OpenAI** credential:
   ```
   Name: OpenAI API
   API Key: [Your OpenAI API Key from .env]
   ```

## Step 3: Activate the Workflow

1. Open the imported **BIBBI RAG Business Intelligence Chat** workflow
2. Click **Save** to save the workflow
3. Click **Activate** to make the webhook live
4. Note the webhook URL (will be something like):
   ```
   https://your-n8n-instance.com/webhook/bibbi-chat
   ```

## Step 4: Test the Webhook

### 4.1 Test with curl
```bash
curl -X POST "https://your-n8n-instance.com/webhook/bibbi-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my total sales?",
    "userId": "test-user",
    "sessionId": "test-session"
  }'
```

### 4.2 Expected Response
```json
{
  "success": true,
  "message": "Your total sales are €4,657.48 across 126 records from 7 different resellers.",
  "questionType": "total_sales",
  "timestamp": "2025-01-07T22:00:00.000Z",
  "data": {
    "summary": {
      "totalSales": 4657.48,
      "totalRecords": 126,
      "uniqueResellers": 7
    }
  },
  "metadata": {
    "originalQuestion": "What are my total sales?",
    "processingTime": 1250,
    "dataPoints": 3
  }
}
```

## Step 5: Frontend Integration

### 5.1 Update Your Frontend
Replace the existing chat API call with the n8n RAG service:

```javascript
// In your ChatInterface component
import N8nRagService from '../services/n8n_integration.js';

const ragService = new N8nRagService('https://your-n8n-instance.com/webhook/bibbi-chat');

// Replace sendChatQuery call with:
const response = await ragService.askQuestion(inputMessage, userId, sessionId);
```

### 5.2 Update Environment Variables
Add to your `.env` file:
```bash
# n8n RAG Configuration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/bibbi-chat
N8N_TIMEOUT=30000
```

## Step 6: Advanced Configuration

### 6.1 Customize Business Context
In the **Generate AI Response** node, you can customize the system prompt:
- Update business terminology
- Add specific product knowledge
- Include company-specific insights
- Modify response tone and style

### 6.2 Add More Data Sources
To include additional tables:
1. Update the **Query Builder** node
2. Add new query types in the switch statement
3. Update the **Execute Supabase Query** node
4. Modify the **Data Aggregator** to handle new data types

### 6.3 Enable Conversation Memory
The workflow includes session handling. To enhance memory:
1. Store conversation history in Supabase
2. Include recent questions in the AI prompt
3. Use vector embeddings for semantic similarity

## Step 7: Testing Different Question Types

### Direct Answer Questions:
- "What are my total sales?"
- "Who is my top reseller?"
- "How many products do I have?"
- "Which month had the highest sales?"

### Table Display Questions:
- "Show me all my resellers"
- "List my top 10 products"
- "Give me a breakdown by month"
- "Analyze sales by region"

### Business Intelligence Questions:
- "How is business performing this quarter?"
- "What are my best selling products this year?"
- "Which reseller has grown the most?"
- "Show me sales trends over time"

## Step 8: Monitoring and Debugging

### 8.1 n8n Execution Log
- View execution history in n8n
- Check for errors in individual nodes
- Monitor processing times

### 8.2 Frontend Debugging
- Check browser console for request/response logs
- Use the debug toggle to see processing details
- Monitor network requests in dev tools

## Step 9: Production Deployment

### 9.1 n8n Cloud (Recommended)
- Sign up for n8n Cloud
- Import your workflow
- Configure credentials
- Get production webhook URL

### 9.2 Self-Hosted n8n
- Deploy n8n on your server
- Configure SSL/HTTPS
- Set up proper authentication
- Configure backup and monitoring

## Troubleshooting

### Common Issues:

1. **Webhook not responding**
   - Check n8n is running
   - Verify workflow is activated
   - Check credentials are configured

2. **Supabase connection errors**
   - Verify Supabase URL and keys
   - Check RLS policies allow service access
   - Test queries in Supabase dashboard

3. **OpenAI API errors**
   - Verify API key is valid
   - Check usage limits
   - Monitor API rate limits

4. **Slow responses**
   - Optimize Supabase queries
   - Reduce data processing
   - Implement caching

## Benefits of n8n RAG vs Current System

| Feature | Current System | n8n RAG System |
|---------|---------------|----------------|
| Question Understanding | Pattern matching | AI-powered classification |
| Data Sources | Single table | Multi-table queries |
| Response Quality | Template-based | Context-aware AI |
| Conversation Memory | None | Session-based memory |
| Business Context | Limited | Rich business intelligence |
| Error Handling | Basic | Comprehensive fallbacks |
| Debugging | Console logs | Full execution history |
| Scalability | Limited | Highly scalable |

## Next Steps

1. **Import and test** the workflow
2. **Customize** the business prompts
3. **Integrate** with your frontend
4. **Test** with various question types
5. **Monitor** performance and optimize
6. **Scale** to production environment

The n8n RAG system will provide a much more intelligent and business-aware chat experience compared to the current SQL-based approach!