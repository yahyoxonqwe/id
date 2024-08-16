import mysql.connector

# Replace these with your actual database credentials
db_name = 'database2'
db_user = 'root'
db_password = 'Airi123'
db_host = 'localhost'           # Use 'localhost' to connect via TCP/IP
db_port = 3306
# Connect to your MySQL database
conn = mysql.connector.connect(
    database=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
cursor = conn.cursor()

# Execute the SQL query to create the table
cursor.execute("""
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    arrival_time TIMESTAMP,
    departure_time TIMESTAMP,
    times TEXT,
    count INT DEFAULT 1,
    image TEXT
);
""")

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()