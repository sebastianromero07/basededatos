# archivo database.py
import psycopg2
from psycopg2 import pool

def connect():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='proyecto',
            port='5432',
            user='postgres',
            password='Sebrom@20'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Pool de conexiones para mejorar la eficiencia
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,  # Minimo de conexiones
    10, # Maximo de conexiones
    host='localhost',
    dbname='proyecto',
    port='5432',
    user='postgres',
    password=''
)

def get_connection():
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        return None

def release_connection(conn):
    try:
        connection_pool.putconn(conn)
    except Exception as e:
        print(f"Error releasing connection back to pool: {e}")
