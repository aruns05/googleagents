import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector

from sqlalchemy import text



# initialize Cloud SQL Python Connector
connector = Connector()

# create connection pool engine
engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=lambda: connector.connect(
        "energymgmt-461218:us-central1:pdlcsandbox", # Cloud SQL Instance Connection Name
        "pg8000",
        user="arun",
        password="Mayurvihar@011",
        db="pdlc",
        ip_type="public"  # "private" for private IP
    ),
)

# Assuming 'engine' is already created as in the script above
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM pdlcmemory"))
    print("Found sessions via raw SQL:")
    for row in result:
        print(f"  - Session ID: {row.session_id}, User ID: {row.user_id}")
        





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