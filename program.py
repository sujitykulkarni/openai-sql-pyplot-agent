from typing import Any, cast
import atexit
from agents import (
    Agent,
    RunResult,
    Runner,
    set_default_openai_client,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from agents.mcp import MCPServer, MCPServerStdio
import os
import shutil
from dotenv import load_dotenv
from openai_client import client, AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL
import asyncio
import sys
import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)

# Optionally silence stderr during shutdown
original_stderr = sys.stderr


def silence_stderr_on_exit():
    sys.stderr = open(os.devnull, 'w')


atexit.register(silence_stderr_on_exit)

# Load environment variables
load_dotenv()

# Load environment variables for Azure OpenAI (deployment model is provided by openai_client)
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

# Load environment variables for SQL MCP server (use string defaults to satisfy type checks)
SERVER_NAME = os.getenv("SERVER_NAME", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "")
AUTH_METHOD = os.getenv("AUTH_METHOD", "sql")
SQL_USERNAME = os.getenv("SQL_USERNAME", "")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
READONLY = os.getenv("READONLY", "false")
CONNECTION_TIMEOUT = os.getenv("CONNECTION_TIMEOUT", "50")
TRUST_SERVER_CERTIFICATE = os.getenv("TRUST_SERVER_CERTIFICATE", "true")

# `client` and model name are imported from `openai_client.py` and shared across modules

# Disable tracing
set_tracing_disabled(disabled=True)


async def run_agent_with_sql_server(sql_server: MCPServer, instructions: str, user_input: str) -> RunResult:
    """Run the agent with the SQL MCP server"""

    agent = Agent(
        name="SQL Automation Agent",
        instructions=instructions,
        mcp_servers=[sql_server],
        model=OpenAIChatCompletionsModel(
            model=cast(str, AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL),
            openai_client=client
        ),
    )

    result = await Runner.run(
        starting_agent=agent,
        input=user_input,
        max_turns=50
    )
    print(f"SQL Agent execution completed with result: {result.final_output}")

    return result


async def main(user_input: str | None = None) -> RunResult | None:
    """Main function to run the SQL agent"""
    if user_input is None:
        print("Please provide a user input query.")
        return
    # Check for Node.js installation for the SQL MCP server
    if not shutil.which("node"):
        print("Error: node is not installed. Please install Node.js and try again.")
        return

    # Load instructions from file
    try:
        with open("sql_system_instructions.txt", "r", encoding="utf-8") as f:
            instructions = f.read().strip()
    except FileNotFoundError:
        print("Error: sql_system_instructions.txt file not found.")
        return
    except Exception as e:
        print(f"Error reading instructions file: {e}")
        return

    # user_input = "Show me the top 10 products by total sales value, including the product name, category, and the total revenue for each, ordered from highest to lowest revenue"

    try:
        # Use the specific Node.js MCP server

        async with MCPServerStdio(
            name="SQL Server MCP",
            client_session_timeout_seconds=30,
            params={
                "command": "node",
                "args": ["D:\\repo\\SQL-AI-samples\\MssqlMcp\\Node\\dist\\index.js"],
                "env": {
                    "SERVER_NAME": SERVER_NAME,
                    "DATABASE_NAME": DATABASE_NAME,
                    "AUTH_METHOD": AUTH_METHOD,
                    "SQL_USERNAME": SQL_USERNAME,
                    "SQL_PASSWORD": SQL_PASSWORD,
                    "READONLY": READONLY,
                    "CONNECTION_TIMEOUT": CONNECTION_TIMEOUT,
                    "TRUST_SERVER_CERTIFICATE": TRUST_SERVER_CERTIFICATE
                }
            },
            cache_tools_list=True
        ) as sql_server:
            # Test MCP server connection
            try:
                # List the tools for the SQL server
                sql_tools = await sql_server.list_tools()
                if not sql_tools:
                    print("Error: No tools available from MCP server")
                    return
            except Exception as e:
                print(f"Error connecting to MCP server: {e}")
                return

            # Run the agent with the SQL server
            result = await run_agent_with_sql_server(sql_server, instructions, user_input)

            return result

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
