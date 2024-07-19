import sqlite3 

def create_table():
    # Connect to the SQLite database named 'scores.db'
    # If the database does not exist, it will be created
    conn = sqlite3.connect('scores.db')
    
    # Create a cursor object which allows us to execute SQL commands
    cursor = conn.cursor()
    
    # Execute a SQL command to create a table named 'scores' if it does not already exist
    # The table has columns: id (integer primary key), score (integer), date (text),
    # shots (integer), hits (integer), and accuracy (real number)
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                      (id INTEGER PRIMARY KEY, 
                       score INTEGER, 
                       date TEXT, 
                       shots INTEGER, 
                       hits INTEGER, 
                       accuracy REAL)''')
    
    # Commit the changes to the database
    conn.commit()
    
    # Close the connection to the database
    conn.close()
