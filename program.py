from agents import (
    Agent, 
    Runner,
    set_default_openai_client,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from agents.mcp import MCPServer, MCPServerStdio
import os
import shutil
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
import asyncio
import sys
import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)

# Optionally silence stderr during shutdown
original_stderr = sys.stderr

def silence_stderr_on_exit():
    sys.stderr = open(os.devnull, 'w')

import atexit
atexit.register(silence_stderr_on_exit)

# Load environment variables
load_dotenv()

# Load environment variables for Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Load environment variables for SQL MCP server
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
AUTH_METHOD = os.getenv("AUTH_METHOD", "sql")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
READONLY = os.getenv("READONLY", "false")
CONNECTION_TIMEOUT = os.getenv("CONNECTION_TIMEOUT", "50")
TRUST_SERVER_CERTIFICATE = os.getenv("TRUST_SERVER_CERTIFICATE", "true")

# Configure Azure OpenAI client
try:
    client = AsyncAzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION
    )
except Exception as e:
    print(f"Error configuring Azure OpenAI client: {e}")
    sys.exit(1)

# Configure the default OpenAI client
set_default_openai_client(client)

# Disable tracing
set_tracing_disabled(disabled=True)

async def run_agent_with_sql_server(sql_server: MCPServer, instructions: str, user_input: str) -> None:
    """Run the agent with the SQL MCP server"""

    agent = Agent(
        name="SQL Automation Agent",
        instructions=instructions,
        mcp_servers=[sql_server],
        model=OpenAIChatCompletionsModel(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL,
            openai_client=client
        )
    )

    result = await Runner.run(
        starting_agent=agent,
        input=user_input,
        max_turns=50
    )
    print(f"SQL Agent execution completed with result: {result.final_output}")

async def main():
    """Main function to run the SQL agent"""
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

    user_input = "Show me the first 5 rows from the Customer table"

    try:
        # Use the specific Node.js MCP server

        async with MCPServerStdio(
            name="SQL Server MCP",
            client_session_timeout_seconds=30,
            params={
                "command": "node",
                "args": ["D:/Research/sql-mcp-integration/repo/SQL-AI-samples/MssqlMcp/Node/dist/index.js"],
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
            await run_agent_with_sql_server(sql_server, instructions, user_input)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")

