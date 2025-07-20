# SQL MCP Integration with Azure OpenAI

## Overview

This project demonstrates how to integrate Azure SQL Database with Azure OpenAI using the Model Context Protocol (MCP) server architecture. The solution enables natural language querying of SQL databases through AI agents, providing an intelligent interface for database operations.

## Architecture

The project follows a client-server architecture using the Model Context Protocol (MCP):

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Azure OpenAI  │    │   Python Agent   │    │   SQL MCP       │
│   (GPT-4/GPT-3.5│◄──►│   (Client)       │◄──►│   Server        │
│   -turbo)       │    │                  │    │   (Node.js)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Azure SQL     │
                                              │   Database      │
                                              └─────────────────┘
```

### Components

1. **Azure OpenAI Service**: Provides the AI model (GPT-4 or GPT-3.5-turbo) for natural language processing
2. **Python Agent**: Acts as the MCP client, orchestrating communication between AI and SQL server
3. **SQL MCP Server**: Node.js-based MCP server that handles SQL database operations
4. **Azure SQL Database**: The target database for queries and operations

## Features

- **Natural Language Queries**: Convert plain English to SQL queries
- **Intelligent Database Operations**: Execute complex database operations through AI
- **Secure Connection**: Support for SQL authentication with Azure SQL
- **Read-only Mode**: Optional read-only access for safety
- **Connection Management**: Configurable timeouts and certificate handling

## Prerequisites

- Python 3.8+
- Node.js 16+
- Azure OpenAI Service account
- Azure SQL Database
- Required Python packages (see `requirements.txt`)

## ⚠️ IMPORTANT: Updated MCP Server Setup

This repository includes an **updated version** of the SQL MCP server with support for multiple authentication methods. The original Azure SQL-AI-samples repository only supports Azure AD authentication, but this enhanced version adds support for:

- **SQL Server Authentication** (username/password)
- **Windows Authentication** (NTLM)
- **Azure AD Authentication** (original method)

### Setup Instructions:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sql-mcp-integration
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the enhanced MCP server**:
   ```bash
   # Clone the original SQL-AI-samples repository
   git clone https://github.com/Azure-Samples/SQL-AI-samples.git repo/SQL-AI-samples
   
   # Navigate to the Node.js MCP server directory
   cd repo/SQL-AI-samples/MssqlMcp/Node
   
   # Install dependencies
   npm install

   After the build is successful, locate the index.js file within the newly created dist folder. Copy and save its fully qualified path. you will need in an upcoming step.

   
   # ⚠️ CRITICAL: Replace the generated index.js with our updated version
   # Copy the enhanced index.ts from this repository to replace the original
   cp ../../../index.ts src/index.ts
   
   ```

4. **Verify the enhanced features**:
   The enhanced `index.ts` file includes:
   - Multi-authentication support (SQL, Windows, Azure AD)
   - Better error handling and debugging
   - Configurable connection timeouts
   - Enhanced logging for troubleshooting

5. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_CHAT_DEPLOYMENT=your_deployment_name
   AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL=gpt-4
   AZURE_OPENAI_API_VERSION=2024-02-15-preview

   # SQL Database Configuration
   SERVER_NAME=your_sql_server.database.windows.net
   DATABASE_NAME=your_database_name
   AUTH_METHOD=sql
   SQL_USERNAME=your_username
   SQL_PASSWORD=your_password
   READONLY=false
   CONNECTION_TIMEOUT=50
   TRUST_SERVER_CERTIFICATE=true
   ```

## Usage

### Basic Usage

Run the main program:
```bash
python program.py
```

The program will:
1. Connect to the SQL MCP server
2. Initialize the AI agent with SQL capabilities
3. Execute the default query: "Show me the first 5 rows from the Customer table"

### Custom Queries

To run custom queries, modify the `user_input` variable in `program.py`:

```python
user_input = "Find all customers who made purchases in the last 30 days"
```

### System Instructions

The AI agent uses system instructions defined in `sql_system_instructions.txt`. This file contains guidelines for:
- How to interpret natural language queries
- SQL best practices
- Error handling
- Security considerations

## Project Structure

```
sql-mcp-integration/
├── program.py                      # Main application entry point
├── sql_system_instructions.txt     # AI agent system instructions
├── requirements.txt                # Python dependencies
├── index.ts                        # Enhanced MCP server with multi-auth support
├── .env                           # Environment variables (create this)
├── readme.md                      # This documentation
└── repo/
    └── SQL-AI-samples/            # Original Azure SQL-AI-samples repository
        └── MssqlMcp/
            └── Node/
                ├── dist/
                │   └── index.js   # Compiled SQL MCP server (replace with enhanced version)
                ├── src/           # Source code
                ├── package.json   # Node.js dependencies
                └── tsconfig.json  # TypeScript configuration
```

## Configuration Options

### Azure OpenAI Settings

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: Deployment name for chat completions
- `AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL`: Model name (e.g., gpt-4, gpt-35-turbo)
- `AZURE_OPENAI_API_VERSION`: API version to use

### SQL Database Settings

- `SERVER_NAME`: Azure SQL server name
- `DATABASE_NAME`: Target database name
- `AUTH_METHOD`: Authentication method (sql, azure-ad, etc.)
- `SQL_USERNAME`: Database username
- `SQL_PASSWORD`: Database password
- `READONLY`: Set to "true" for read-only access
- `CONNECTION_TIMEOUT`: Connection timeout in seconds
- `TRUST_SERVER_CERTIFICATE`: Whether to trust server certificate

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Read-only Mode**: Use read-only mode for production queries when possible
3. **Connection Security**: Ensure proper SSL/TLS configuration
4. **API Key Management**: Use Azure Key Vault for API key storage in production

## Troubleshooting

### Common Issues

1. **Node.js not found**: Ensure Node.js is installed and in PATH
2. **Connection timeout**: Check network connectivity and firewall settings
3. **Authentication errors**: Verify SQL credentials and permissions
4. **MCP server errors**: Check the Node.js MCP server logs

### Debug Mode

Enable debug logging by modifying the Python code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Azure SQL and OpenAI documentation
3. Open an issue in the repository

## Related Documentation

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/)
- [MCP Server Development](https://modelcontextprotocol.io/docs/server-overview)
