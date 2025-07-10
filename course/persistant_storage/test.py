import sqlite3

# Connect to the SQLite database
# If the file does not exist, it will create a new database
connection = sqlite3.connect('sample.db')

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Example: Read data from a table named 'example_table'
try:
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()

    # Print the rows
    for row in rows:
        print(row)

except sqlite3.OperationalError as e:
    print(f"An error occurred: {e}")

# Close the connection
connection.close()


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