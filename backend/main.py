from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import QuestionRequest, AnalysisResponse
from backend.agent import run_agent

app = FastAPI(
    title="AI Data Analyst API",
    description="Ask questions about sales data in plain English.",
    version="1.0.0",
)

# CORS — allows Streamlit (port 8501) to call this API (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Quick check that the server is running."""
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: QuestionRequest):
    """
    Main endpoint. Receives a question, runs the agent,
    returns answer + SQL + chart + reasoning.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_agent(request.question)

    return AnalysisResponse(
        answer=result["final_answer"],
        sql_query=result["sql_query"],
        chart_json=result["chart_json"],
        reasoning=result["reasoning"],
    )