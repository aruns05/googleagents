import psycopg2

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector

DB_HOST = "34.30.106.150" # e.g., '127.0.0.1' for proxy, or public IP
DB_USER = "arun"
DB_PASSWORD = "Mayurvihar@011"
DB_NAME = "pdlc" # e.g., 'pdlc' if that's your database name
DB_PORT = "5432" # Default PostgreSQL port

connection_string = (
    f"host={DB_HOST} "
    f"dbname={DB_NAME} "
    f"user={DB_USER} "
    f"password={DB_PASSWORD} "
    f"port={DB_PORT}"
)

try:
    print("Connecting to the database...")
    # conn = psycopg2.connect(
    #     host=DB_HOST,
    #     dbname=DB_NAME,
    #     user=DB_USER,
    #     password=DB_PASSWORD,
    #     port=DB_PORT
    # )
    
    # create connection pool engine
engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=lambda: connector.connect(
        "project:region:instance-name", # Cloud SQL Instance Connection Name
        "pg8000",
        user="my-user",
        password="my-password",
        db="my-database",
        ip_type="public"  # "private" for private IP
    ),
)
    
 
    #conn = psycopg2.connect(connection_string)

    #34.30.106.150
    print("Connected to the database successfully")
    cur = conn.cursor()
    print("here1")
    cur.execute('SELECT * FROM pdlcmemory;')
    rows = cur.fetchall()
    #conn.commit()
    conn.close()
    for row in rows:
        print(row)
        
except psycopg2.OperationalError as e:
    # It's better to catch more specific exceptions
    print(f"An error occurred while connecting to the database: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Using a finally block ensures the connection is closed
    # even if an error occurs after it's established.
    # if conn:
    #     conn.close()
    #     print("Database connection closed.") 
                
        





# import sqlite3

# # Connect to the SQLite database
# # If the file does not exist, it will create a new database
# connection = sqlite3.connect('sample.db')

# # Create a cursor object to interact with the database
# cursor = connection.cursor()

# # Example: Read data from a table named 'example_table'
# try:
#     cursor.execute("SELECT * FROM sessions")
#     rows = cursor.fetchall()

#     # Print the rows
#     for row in rows:
#         print(row)

# except sqlite3.OperationalError as e:
#     print(f"An error occurred: {e}")

# # Close the connection
# connection.close()


# sessions
# app_states
# user_states
# events

# import sqlite3

# # Connect to the SQLite database
# connection = sqlite3.connect('sample.db')

# # Create a cursor object to interact with the database
# cursor = connection.cursor()

# # Query to get all table names
# try:
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cursor.fetchall()

#     # Print the table names
#     print("Tables in the database:")
#     for table in tables:
#         print(table[0])

# except sqlite3.OperationalError as e:
#     print(f"An error occurred: {e}")

# # Close the connection
# connection.close()