import datetime
from zoneinfo import ZoneInfo
import sqlite3
import matplotlib.pyplot as plt
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
    

schema_agent = Agent(
    name="schema_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "An intelligent agent specialized in retrieving the schema of an SQLite database. "
        "It helps users understand the structure of their database by extracting table names, "
        "columns, and data types based on natural language prompts."
    ),
    instruction=(
        "You can ask me to describe the structure of your SQLite database. "
        "I'll return details like table names, column names, and data types."
    ),
    tools=[get_database_schema]
)


operation_agent = Agent(
    name="operation_agent",
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
    tools=[interact_with_sql_database]
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "You are the Root Agent responsible for coordinating a team of specialized agents to handle natural language "
        "interactions with an SQLite database.\n\n"
        "- For any SQL-related request:\n"
        "  • First, invoke the `schema_agent` to understand the structure of the database (table names, columns, and data types).\n"
        "  • Then, provide this schema context to the `operation_agent`, who will generate or execute the appropriate SQL queries.\n\n"
        "Your role is to manage this flow, ensuring the schema is retrieved before any query operations are attempted. "
        "If a request falls outside database-related tasks, clearly state that you cannot handle it."
    ),
    instruction=(
        "When a user asks a question:\n"
        f"- First, call {schema_agent} to get the full schema (see if it is related to the database).\n"
        f"- Then, pass the schema and the user's original request to {operation_agent} to fulfill the task.\n"
    ),
    sub_agents=[schema_agent, operation_agent]
)

