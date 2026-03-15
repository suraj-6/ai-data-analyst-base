
# AI Data Analyst Agent

An AI agent that answers natural language questions about sales data by 
generating SQL, querying a database, and returning interactive charts.

## Demo
> "Which product had the highest revenue in March?"

The agent:
1. Generates SQL using GPT-4o
2. Queries a SQLite database
3. Builds a Plotly chart
4. Returns a natural language answer with reasoning steps

## Tech Stack
- **Agent**: LangGraph + LangChain
- **LLM**: OpenAI GPT-4o
- **Backend**: FastAPI + Python
- **Database**: SQLite + Pandas
- **Frontend**: Streamlit + Plotly

## Project Structure
```
ai-data-analyst/
├── backend/
│   ├── agent.py       # LangGraph agent with 4 nodes
│   ├── tools.py       # SQL executor + chart builder
│   ├── database.py    # SQLite connection
│   ├── main.py        # FastAPI REST API
│   └── schemas.py     # Pydantic models
├── frontend/
│   └── app.py         # Streamlit chat UI
└── data/
    └── seed.py        # Database seeder
```

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your OpenAI key
python data/seed.py         # seed the database
```

## Run
```bash
# Terminal 1
uvicorn backend.main:app --reload --port 8000

# Terminal 2
streamlit run frontend/app.py
```

Open http://localhost:8501
```

Also create `.env.example` — a safe template without real secrets:
```
OPENAI_API_KEY=sk-your-key-here
