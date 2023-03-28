import psycopg2
import os
from dotenv import load_dotenv
import datetime


load_dotenv()
conn = psycopg2.connect(
        dbname=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD'),
        host=os.getenv('DATABASE_IP'),
        port=os.getenv('DATABASE_PORT')
    )

cur = conn.cursor()
try:
    cur.execute("CREATE TABLE home_monitor (t_stamp timestamp, co2 real, hum real, temp real);")
    conn.commit()
except:
    print("database already created")
    conn.rollback()

now = datetime.datetime.now()
cur.execute("INSERT INTO home_monitor (t_stamp, co2, hum, temp) VALUES ('" + str(now) + "', 450.0, 50.0, 23.5)")
conn.commit()
cur.execute("SELECT * from home_monitor")
data = cur.fetchall()
for i in data:
    print(i)
conn.close()
cur.close()
