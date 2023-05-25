import psycopg2
import os
from dotenv import load_dotenv
import datetime
import logging
from uart import Device
import asyncio


def get_connection():
    conn = psycopg2.connect(
            dbname=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            host=os.getenv('DATABASE_IP'),
            port=os.getenv('DATABASE_PORT')
        )
    return conn


def list_all_rows():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * from home_monitor")
    data = cur.fetchall()
    print(' ')
    for i in data:
        print(i)
    conn.close()
    cur.close()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("sql.log"),
            logging.StreamHandler()
        ]
    )

    load_dotenv()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE TABLE home_monitor (t_stamp timestamp, co2 real, hum real, temp real);")
        conn.commit()
    except psycopg2.errors.DuplicateTable:
        logging.info("database already created")
        conn.rollback()

    devices = Device.get_devices()

    for d in devices:
        if d.type == 'HUM':
            hum_probe = d
        elif d.type == 'CO2':
            co2_probe = d
    while True:
        try:
            co2 = co2_probe.get_reading()
            if co2 is None:
                co2 = "Null"
            hum, temp = hum_probe.get_reading()
            now = datetime.datetime.now()
            sql_insert = "INSERT INTO home_monitor (t_stamp, co2, hum, temp) VALUES ('" + str(now) + "', " + str(co2) + ", " + str(hum) + ", " + str(temp) + ")"
            logging.info(sql_insert)
            cur.execute(sql_insert)
            conn.commit()
        except (TypeError, psycopg2.errors.UndefinedColumn) as e:
            logging.error(str(e))
        list_all_rows()
        await asyncio.sleep(300)
    conn.close()
    cur.close()

if __name__ == "__main__":
    asyncio.run(main())
