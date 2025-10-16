import pandas as pd
from psycopg2 import connect

DB_CONFIG = {
    "dbname": "PhonePayDB",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

def run_query(sql_text, params=None):
    with connect(**DB_CONFIG) as conn:
        return pd.read_sql(sql_text, conn, params=params)
