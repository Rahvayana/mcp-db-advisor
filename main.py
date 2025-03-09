from mcp.server.fastmcp import FastMCP
import mysql.connector
import psycopg2
from typing import Dict, Union
import json

# Global connection config
DB_CONFIG: Dict[str, str] = {}
DB_TYPE: str = None

mcp = FastMCP("DatabaseAdvisor")

# Tool to set up the database connection
@mcp.tool()
def connect_to_database(type: str, user: str, password: Union[str, int], host: str, port: Union[str, int], database: str) -> str:
    """
    Connect to a SQL database using the provided credentials.
    Automatically detects MySQL or PostgreSQL based on type.
    
    Args:
        type: Database type ('mysql' or 'postgresql')
        user: Database username
        password: Database password (string or integer)
        host: Database host (e.g., 'localhost')
        port: Database port (e.g., 3306 for MySQL, 5432 for PostgreSQL, as string or integer)
        database: Database name
    
    Example prompt:
        "Connect to database with type:mysql user:user password:passw host:localhost port:3306 database:my_database"
    
    Returns:
        JSON string with connection status, database type, and available tables
    """
    global DB_CONFIG, DB_TYPE
    DB_TYPE = type.lower()
    
    # Convert port and password to strings if they’re integers
    port_str = str(port)
    password_str = str(password)
    
    # Build the config dictionary
    DB_CONFIG = {
        "user": user,
        "password": password_str,
        "host": host,
        "port": port_str,
        "database": database
    }
    
    # Test the connection and get table list
    try:
        conn = get_connection()
        cursor = conn.cursor()
        tables = []
        if DB_TYPE == "mysql":
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        elif DB_TYPE == "postgresql":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            return json.dumps({"status": "error", "message": "Unsupported database type. Use 'mysql' or 'postgresql'."})
        conn.close()
        
        return json.dumps({
            "status": "success",
            "database_type": DB_TYPE,
            "database": database,
            "tables": tables
        })
    except Exception as e:
        DB_CONFIG = {}  # Reset on failure
        DB_TYPE = None
        return json.dumps({"status": "error", "message": str(e)})

# Helper function to get disconnect
@mcp.tool()
def disconnect_database() -> str:
    """
    Disconnects from the current database connection.
    
    Returns:
        Confirmation message as a string
    """
    global DB_CONFIG, DB_TYPE
    if not DB_CONFIG or not DB_TYPE:
        return "No active connection to disconnect"
    DB_CONFIG = {}
    DB_TYPE = None
    return "Disconnected from the database successfully"

# Helper function to get a connection
def get_connection():
    if not DB_CONFIG or not DB_TYPE:
        raise Exception("No database connection defined. Use 'connect_to_database' first.")
    if DB_TYPE == "mysql":
        return mysql.connector.connect(**DB_CONFIG)
    elif DB_TYPE == "postgresql":
        return psycopg2.connect(**DB_CONFIG)
    else:
        raise Exception("Unsupported database type.")

# Existing Resource
@mcp.resource("schema://main")
def get_schema() -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if DB_TYPE == "mysql":
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            schema = []
            for table in tables:
                cursor.execute(f"SHOW CREATE TABLE {table}")
                schema.append(cursor.fetchone()[1])
            conn.close()
            return "\n\n".join(schema)
        elif DB_TYPE == "postgresql":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
            schema = []
            for table in tables:
                cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table,))
                columns = "\n".join(f"{row[0]}: {row[1]}" for row in cursor.fetchall())
                schema.append(f"Table: {table}\n{columns}")
            conn.close()
            return "\n\n".join(schema)
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

# Existing Tools (unchanged, just using get_connection)
@mcp.tool()
def run_query(query: str) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor.description:
            results = cursor.fetchall()
            conn.close()
            return "\n".join(str(row) for row in results)
        else:
            conn.commit()
            conn.close()
            return "Query executed successfully"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

@mcp.tool()
def suggest_optimization(query: str) -> str:
    suggestions = []
    query_lower = query.lower()
    if "select *" in query_lower and "where" not in query_lower:
        suggestions.append("Avoid 'SELECT *' without a WHERE clause.")
    if "where" in query_lower:
        suggestions.append("Ensure indexed columns are used in WHERE.")
    return "\n".join(suggestions) or "No optimizations detected."

@mcp.tool()
def explain_query(query: str) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN {query}")
        plan = cursor.fetchall()
        conn.close()
        return "\n".join(str(row) for row in plan)
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

# Additional Tools (unchanged, just using get_connection)
@mcp.tool()
def create_table(table_name: str, columns: str) -> str:
    query = f"CREATE TABLE {table_name} ({columns})"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return f"Table '{table_name}' created successfully"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

@mcp.tool()
def add_column(table_name: str, column_def: str) -> str:
    query = f"ALTER TABLE {table_name} ADD COLUMN {column_def}"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return f"Column added to '{table_name}' successfully"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

@mcp.tool()
def add_foreign_key(table: str, column: str, ref_table: str, ref_column: str) -> str:
    query = f"ALTER TABLE {table} ADD FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return f"Foreign key added to '{table}.{column}' referencing '{ref_table}.{ref_column}'"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

@mcp.tool()
def drop_table(table_name: str) -> str:
    query = f"DROP TABLE IF EXISTS {table_name}"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return f"Table '{table_name}' dropped successfully"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

@mcp.tool()
def list_tables() -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if DB_TYPE == "mysql":
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            conn.close()
            return "\n".join(row[0] for row in tables)
        elif DB_TYPE == "postgresql":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            conn.close()
            return "\n".join(row[0] for row in tables)
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

@mcp.tool()
def describe_table(table_name: str) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if DB_TYPE == "mysql":
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            conn.close()
            return "\n".join(f"{col[0]}: {col[1]}" for col in columns)
        elif DB_TYPE == "postgresql":
            cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table_name,))
            columns = cursor.fetchall()
            conn.close()
            return "\n".join(f"{col[0]}: {col[1]}" for col in columns)
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()