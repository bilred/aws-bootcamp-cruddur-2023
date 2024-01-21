import json
import psycopg2
from psycopg2 import pool
from urllib.parse import urlparse
import os
import sys


def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes')
    print(user)
  
    user_display_name  = user['name']
    user_email         = user['email']
    user_handle        = user['preferred_username']
    user_cognito_id    = user['sub']

    params = [
        user_display_name,
        user_email,
        user_handle,
        user_cognito_id
    ]      
    
    print('entered-try')
    print(params)
    sql = return_string_sql(*params)

    conn = None
    conn = create_connection()
    execute_query(conn, sql, *params)

    if conn:
        conn.close()
        print('Database connection closed')

def create_connection():
    """ Create a connection to the PostgreSQL database """
    
    print('CONNECTION_URL ----')
    connection_url = os.getenv("CONNECTION_URL")
    print(connection_url)
    
    url_parts = urlparse(connection_url)
    
    # Create a connection pool
    connection_pool = pool.SimpleConnectionPool(
        minconn=1, maxconn=10,
        user=url_parts.username,
        password=url_parts.password,
        host=url_parts.hostname,
        port=url_parts.port,
        database=url_parts.path.lstrip('/'),
    )    
    
    try:
        with connection_pool.getconn() as conn:
            print("Connection to the database successful!")
    except (Exception, psycopg2.DatabaseError) as e:
        print_sql_err(e)
    return conn
    
def return_string_sql(*params):
    sql = f"""
       INSERT INTO public.users (
        display_name, 
        handle,
        email,
        cognito_user_id
        ) 
       VALUES({params[0]},{params[1]},{params[2]},{params[3]})
    """
    print('SQL Statement ----')
    print(sql)
    return sql

def execute_query(conn, query, *params):
    """ Execute a SQL query on the connected database """  
    
    with conn.cursor() as cursor:
        try:
            cursor.execute(query, *params)
            conn.commit()
            print("Query executed successfully!")
        except (Exception, psycopg2.DatabaseError) as e:
            print_sql_err(e)
        finally:
            cursor.close()

def print_sql_err(err):
    # get details about the exception
    err_type, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg ERROR:", err, "on line number:", line_num)
    print ("\npsycopg traceback:", traceback, "-- type:", err_type)
