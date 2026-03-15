import sqlite3
import pandas as pd
import plotly.express as px
import plotly.io as pio
from backend.database import get_connection

def run_sql(query: str) -> dict:
    """
    Execute any SQL SELECT query against the database.
    Returns a dict with success status, column names, and rows as list of dicts.
    The agent calls this after generating SQL.
    """
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()

        return {
            "success": True,
            "columns": df.columns.tolist(),
            "rows": df.to_dict(orient="records"),
            "row_count": len(df),
            "dataframe": df,        # kept in memory, not sent over HTTP
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "rows": [],
            "dataframe": None,
        }


def build_chart(rows: list, question: str) -> dict:
    """
    Given query result rows, pick the best chart type and return Plotly JSON.
    Heuristic:
      - text column + numeric column + few rows  → bar chart
      - text column + numeric column + many rows → line chart
      - only numeric columns                     → bar chart on index
    """
    if not rows:
        return {"chart_json": None, "summary": "Query returned no rows."}

    df = pd.DataFrame(rows)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    string_cols  = df.select_dtypes(include="object").columns.tolist()

    fig = None

    if string_cols and numeric_cols:
        x_col = string_cols[0]
        y_col = numeric_cols[0]
        if len(df) <= 15:
            fig = px.bar(
                df, x=x_col, y=y_col,
                title=question[:80],
                color_discrete_sequence=["#7F77DD"],
            )
        else:
            fig = px.line(
                df, x=x_col, y=y_col,
                title=question[:80],
                markers=True,
            )
    elif numeric_cols:
        fig = px.bar(df, y=numeric_cols[0], title=question[:80])

    if fig:
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=30, l=30, r=30),
        )
        chart_json = pio.to_json(fig)
    else:
        chart_json = None

    # Build a plain-text summary for the answer-writing step
    summary = f"{len(df)} rows returned."
    if numeric_cols:
        col = numeric_cols[0]
        summary += f" {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}."

    return {"chart_json": chart_json, "summary": summary}