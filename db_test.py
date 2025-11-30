import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ishitha!cs2",      # ← use this exact password
        database="steel_factory_db"
    )

    if connection.is_connected():
        print("✅ Connected successfully to MySQL!")
except mysql.connector.Error as e:
    print("❌ Connection failed:", e)
