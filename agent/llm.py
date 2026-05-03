"""
agent/llm.py
Groq LLM wrapper.
Handles natural-language → SQL generation and plain-English explanation.
"""

import json
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> Groq:
    """Return a cached Groq client."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in your .env file.")
        _client = Groq(api_key=api_key)
    return _client


def _model() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def nl_to_sql(question: str, schema: dict) -> str:
    """
    Convert a natural-language question to a SQL SELECT query.
    Injects the full schema so the model knows table/column names.

    Returns raw SQL (no markdown fences).
    """
    schema_str = json.dumps(schema, indent=2)

    system_prompt = f"""You are an expert SQL query writer.

DATABASE SCHEMA:
{schema_str}

STRICT RULES:
1. Return ONLY the raw SQL query — no markdown, no backticks, no explanation.
2. Only write SELECT (or WITH … SELECT) statements.
3. Always use explicit column names; never use SELECT *.
4. Use table aliases for clarity when joining multiple tables.
5. If the question is ambiguous, write the most reasonable interpretation.
6. End the query with a semicolon."""

    response = get_client().chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": question},
        ],
        temperature=0.1,
        max_tokens=512,
    )

    sql = response.choices[0].message.content.strip()
    # Strip any accidental markdown fences
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def explain_sql(sql: str) -> str:
    """
    Translate a SQL query into plain English for a non-technical user.
    Returns 1-2 sentences.
    """
    response = get_client().chat.completions.create(
        model=_model(),
        messages=[
            {
                "role": "user",
                "content": (
                    "Explain what this SQL query does in 1-2 plain-English sentences "
                    "for a non-technical business user. Be concise and specific.\n\n"
                    f"SQL:\n{sql}"
                ),
            }
        ],
        temperature=0.3,
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()


def pick_chart_type(columns: list[str], question: str) -> str:
    """
    Ask the LLM to pick the best chart type for the result set.
    Returns one of: bar, line, pie, scatter, table.
    """
    response = get_client().chat.completions.create(
        model=_model(),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Result columns: {columns}\n"
                    f"Original question: '{question}'\n\n"
                    "Reply with exactly ONE word — the best chart type: "
                    "bar, line, pie, scatter, or table."
                ),
            }
        ],
        temperature=0,
        max_tokens=5,
    )
    raw = response.choices[0].message.content.strip().lower()
    valid = {"bar", "line", "pie", "scatter", "table"}
    return raw if raw in valid else "bar"
