import datetime
from zoneinfo import ZoneInfo
import sqlite3
from google.adk.agents import Agent


def get_database_schema() -> dict:
    """Returns the schema of a specified SQLite database.

    Returns:
        dict: status and result or error msg.
    """
    db_name = "multi_tool_agent/patient_records.db"
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table[0]})")
            schema.append(cursor.fetchall())
        conn.close()
        return {"status": "success", "schema": schema}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def interact_with_sql_database(query: str) -> dict:

    """Executes a specified SQL query on the patient records database.

    Args:
        query (str): The SQL query to execute.

    Returns:
        dict: status and result or error msg.
    """
    try:
        conn = sqlite3.connect('multi_tool_agent/patient_records.db')
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}



root_agent = Agent(
    name="database_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "An intelligent agent designed to query and update SQL databases. "
        "It understands natural language prompts and translates them into SQL operations. "
        "Prioritizes clean, readable, and accurate responses to the user."
    ),
    instruction=(
        "You can ask me to retrieve, update, or analyze data from your database using natural language. "
        "I'll convert your request into a valid SQL query and return or modify the data accordingly."
    ),
    tools=[get_database_schema, interact_with_sql_database]
)
