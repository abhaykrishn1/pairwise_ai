import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Retrieve individual connection parameters from environment variables
snowflake_conn_params = {
    'user': os.getenv("SNOWFLAKE_USER"),
    'password': os.getenv("SNOWFLAKE_PASSWORD"),
    'account': os.getenv("SNOWFLAKE_ACCOUNT"),
    'warehouse': os.getenv("SNOWFLAKE_WAREHOUSE"),
    'database': os.getenv("SNOWFLAKE_DATABASE"),
    'schema': os.getenv("SNOWFLAKE_SCHEMA")
}

def create_snowflake_connector_connection():
    """Create and return a Snowflake connector connection."""
    try:
        return snowflake.connector.connect(**snowflake_conn_params)
    except Exception as e:
        print(f"Error occurred while establishing Snowflake connection: {e}")
        return None

connector_connection = create_snowflake_connector_connection()

if connector_connection:
    print("Snowflake connection established.")
else:
    print("Failed to establish Snowflake connection.")