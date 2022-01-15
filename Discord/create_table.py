import psycopg

import os
from dotenv import load_dotenv

load_dotenv()

# get config from .env file
DB_NAME = os.getenv('POSTGRES_DB_NAME')
DB_USER = os.getenv('POSTGRES_DB_USER')
DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
DB_HOST = os.getenv('POSTGRES_DB_HOST')
DB_PORT = os.getenv('POSTGRES_DB_PORT')

conn = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cur = conn.cursor()

cur.execute("""CREATE TABLE postgres.public.action (
                id serial PRIMARY KEY, 
                user_id bigint not null, 
                created_at TIMESTAMP not null,
                is_unmuted BOOLEAN not null default FALSE,
                count int not null
            );""")

conn.commit()
conn.close()
cur.close()