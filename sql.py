import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
conn = psycopg2.connect(
        dbname=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD'),
        host=os.getenv('DATABASE_IP'),
        port=os.getenv('DATABASE_PORT')
    )

cur = conn.cursor()
