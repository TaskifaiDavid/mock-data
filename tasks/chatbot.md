# 🧠 AI-Powered SQL Chatbot with LangChain (Postgres + GPT-4o)

This guide describes how to build a chatbot that lets users ask natural language questions about data stored in a PostgreSQL database. The backend uses LangChain's SQLDatabaseToolkit with GPT-4o, and the frontend is a floating chat widget available across all pages.

---

## 🧩 Frontend Chat Widget

**Behavior:**
- A circular chat icon is placed in the **bottom-right corner**.
- When clicked, it opens a **popup chat window**.
- Responsive design: works on mobile and desktop.
- Supports **dark/light mode**.
- Messages show in a **clean chat bubble format**.

**User flow:**
1. User types a message (e.g., _“Total sales in 2023?”_)
2. The message is sent to `/api/chat` via POST
3. The AI response is shown in the chat window

**Frontend → Backend Request:**

```json
POST /api/chat
{
  "message": "the user question"
}
Expected Response:

{
  "answer": "response from AI"
}

🧰 Backend with LangChain + SQLDatabaseToolkit
📦 Dependencies
Install with:

pip install langchain langchain-openai psycopg2-binary sqlalchemy fastapi uvicorn python-dotenv
🌐 API Endpoint
Create a FastAPI server with a /api/chat endpoint.

📄 Schema Example
PostgreSQL Table: sellout_entries2

id uuid PRIMARY KEY
product_ean text
month integer
year integer
quantity numeric
sales_lc numeric
sales_eur numeric
currency text
created_at timestamp
reseller text
functional_name text
Use sales_eur for total revenue analysis.

🔌 .env Configuration

OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://user:pass@host:port/dbname
🧠 Backend Logic (FastAPI + LangChain)

from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Connect to DB
db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))

# Setup LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Toolkit and agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)

# Request model
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    response = agent_executor.run(request.message)
    return {"answer": response}


💡 Example Prompts for Users
Users can ask questions like:

"Total sales in 2023?"

"Top 5 resellers by revenue"

"Which reseller sold the most units last month?"

"Monthly sales trend for 2024"

"What was the total quantity sold of product EAN X in March?"

🚀 Deployment Tips
Run backend with:


uvicorn main:app --reload