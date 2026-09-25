import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    connection = psycopg2.connect(DATABASE_URL)

    cursor = connection.cursor()

    cursor.execute("SELECT 1;")

    result = cursor.fetchone()

    print("PostgreSQL connection successful!")
    print("Result:", result)

    cursor.close()
    connection.close()

except Exception as e:
    print("PostgreSQL connection failed!")
    print("Error:", e)