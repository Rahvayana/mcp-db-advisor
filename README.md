# MCP SQL Database Advisor

A Model Context Protocol (MCP) server for Claude Desktop to manage MySQL and PostgreSQL databases.

![MCP SQL Database Advisor](https://github.com/user-attachments/assets/4e6acf98-328f-4f6d-aefd-4d8446ec0a43)


## Features
- Connect/disconnect to MySQL or PostgreSQL
- Run SQL queries
- Create tables, add columns, and manage foreign keys
- Optimize and explain queries
- List and describe tables
- And more...

## Prerequisites
- Python 3.10+
- Claude Desktop [Download here](https://claude.ai/download)
- MySQL or PostgreSQL server

## Configure Claude Desktop
Create a file named `claude_desktop_config.json` in the following location:

- **Windows**: `C:\Users\Username\AppData\Roaming\Claude\claude_desktop_config.json`
- **macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the following content:

```json
{
  "mcpServers": {
    "DatabaseAdvisor": {
      "command": "path/to/env/Scripts/python.exe",
      "args": ["path/to/mcp-db-advisor/main.py"]
    }
  }
}
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Rahvayana/mcp-db-advisor.git
   cd mcp-db-advisor
   ```

2. Set up a virtual environment:
   - **Windows**:
     ```bash
     python -m venv env
     env\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     python -m venv env
     source env/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   mcp dev main.py
   ```

## Usage
After starting the server, open **Claude Desktop** and run:

```
Connect to database with type:mysql user:your_user password:your_pass host:localhost port:3306 database:your_db
```

You can now run SQL queries directly in Claude Desktop.

---

Contributing

Contributions? If you'd like to collaborate, feel free to:

Fork the repository and submit pull requests.

Report issues or suggest features via GitHub Issues.

Reach out if you have ideas for improvements!
Thanks.
---
Now you're all set to use **MCP SQL Database Advisor** with Claude Desktop! 🚀

