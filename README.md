# AI SQL Agent

Ask your database questions in plain English. Powered by **Groq** (Llama 3.3 70B) + **SQLAlchemy** + **Plotly**.
I have used PostgreSQl 
## Features
- Natural language → SQL via Groq LLM
- Plain-English query explanation before execution
- Auto chart generation (bar / line / pie / scatter)
- Query history with JSON persistence
- Safety guard: SELECT-only by default
- Works with PostgreSQL and MySQL

## Project Structure

```
ai_sql_agent/
├── main.py                  ← CLI entry point (run this)
├── requirements.txt
├── .env.example             ← copy to .env and fill in your keys
│
├── agent/
│   ├── db.py                ← DB connection, schema introspection, query runner
│   └── llm.py               ← Groq wrapper: NL→SQL, explanation, chart type picker
│
├── charts/
│   └── renderer.py          ← Plotly auto-chart renderer
│
├── utils/
│   ├── display.py           ← Rich terminal UI helpers
│   └── history.py           ← In-memory + JSON query history
│
├── tests/
│   └── test_db.py           ← pytest unit tests for safety guard
│
└── output/                  ← Created at runtime (charts, history.json)
```

## Quick Start

```bash
# 1. Clone / copy the project
cd ai_sql_agent

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — add your GROQ_API_KEY and DB_URL

# 5. Run the agent
python main.py
```

## Example Session

```
Ask your database: show me total sales by product category last month
Generated SQL: SELECT category, SUM(amount) AS total_sales FROM orders ...
What this query does: This query sums sales amounts grouped by product category ...
Run this query? [Y/n]: Y
┌──────────────┬─────────────┐
│ category     │ total_sales │
├──────────────┼─────────────┤
│ Electronics  │   142500.00 │
│ Clothing     │    98200.00 │
└──────────────┴─────────────┘
Generate chart? [Y/n]: Y   ← opens bar chart in browser
```

## CLI Commands

| Command      | Description                        |
|--------------|------------------------------------|
| `/schema`    | List all tables and columns        |
| `/history`   | Show last 10 queries               |
| `/clear`     | Clear query history                |
| `/help`      | Show available commands            |
| `exit`       | Quit the agent                     |

## Environment Variables

| Variable      | Required | Default                      | Description                   |
|---------------|----------|------------------------------|-------------------------------|
| `GROQ_API_KEY`| Yes      | —                            | Your Groq API key             |
| `DB_URL`      | Yes      | —                            | SQLAlchemy connection string  |
| `GROQ_MODEL`  | No       | `llama-3.3-70b-versatile`    | Groq model to use             |
| `MAX_ROWS`    | No       | `500`                        | Max rows returned per query   |
| `ALLOW_WRITE` | No       | `false`                      | Allow INSERT/UPDATE/DELETE    |

## Running Tests

```bash
pytest tests/ -v
```
