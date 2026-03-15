import os
from dotenv import load_dotenv
from typing import TypedDict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from backend.tools import run_sql, build_chart
from backend.database import get_schema

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

class AgentState(TypedDict):
    question:     str
    sql_query:    str
    query_result: dict
    chart_json:   Optional[str]
    summary:      str
    reasoning:    list[str]
    final_answer: str


def generate_sql_node(state: AgentState) -> AgentState:
    schema = get_schema()
    prompt = f"""You are an expert SQLite analyst.

Database schema:
{schema}

Write a single valid SQLite SELECT query to answer this question:
"{state['question']}"

Rules:
- Output ONLY the SQL query. No explanation, no markdown, no backticks.
- Use strftime('%m', sale_date) for month filtering (e.g. '03' for March).
- Always JOIN products and sales on product_id when product names are needed.
- Always include at least one numeric/aggregated column (e.g. SUM(revenue) AS total_revenue, COUNT(*) AS total_orders) so results have numbers to analyze.
- Never SELECT only text columns — always pair them with a calculated metric.
- Use aliases for clarity (e.g. SUM(revenue) AS total_revenue).
- For "most", "highest", "top" questions return ALL rows with their metrics ordered descending, not just LIMIT 1.

SQL:"""


    response = llm.invoke([HumanMessage(content=prompt)])
    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    state["sql_query"] = sql
    state["reasoning"].append(f"Generated SQL:\n{sql}")
    return state


def run_query_node(state: AgentState) -> AgentState:
    result = run_sql(state["sql_query"])
    if result["success"]:
        state["reasoning"].append(f"Query succeeded. {result['row_count']} rows returned.")
    else:
        state["reasoning"].append(f"Query failed: {result['error']}")
    state["query_result"] = result
    return state


def visualize_node(state: AgentState) -> AgentState:
    if not state["query_result"].get("success"):
        state["summary"] = "No data to visualize — query failed."
        state["chart_json"] = None
        return state
    viz = build_chart(
        rows=state["query_result"]["rows"],
        question=state["question"],
    )
    state["chart_json"] = viz["chart_json"]
    state["summary"] = viz["summary"]
    state["reasoning"].append(f"Visualization built. {viz['summary']}")
    return state


def compose_answer_node(state: AgentState) -> AgentState:
    prompt = f"""You are a business data analyst. Answer the question below in 2-3 clear sentences.
Use the data summary to be specific with numbers.

Question: {state['question']}
Data summary: {state['summary']}
SQL used: {state['sql_query']}

Write a direct, helpful answer:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    state["final_answer"] = response.content.strip()
    state["reasoning"].append("Final answer composed.")
    return state


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("generate_sql",   generate_sql_node)
    graph.add_node("run_query",      run_query_node)
    graph.add_node("visualize",      visualize_node)
    graph.add_node("compose_answer", compose_answer_node)
    graph.set_entry_point("generate_sql")
    graph.add_edge("generate_sql",   "run_query")
    graph.add_edge("run_query",      "visualize")
    graph.add_edge("visualize",      "compose_answer")
    graph.add_edge("compose_answer", END)
    return graph.compile()


agent = build_agent()


def run_agent(question: str) -> dict:
    initial_state: AgentState = {
        "question":     question,
        "sql_query":    "",
        "query_result": {},
        "chart_json":   None,
        "summary":      "",
        "reasoning":    [],
        "final_answer": "",
    }
    return agent.invoke(initial_state)
