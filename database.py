import psycopg2
import os
import csv

# Try to get from system enviroment variable
# Set your Postgres user and password as second arguments of these two next function calls
user = os.environ.get('PGUSER', 'mads')
password = os.environ.get('PGPASSWORD', '1234')
host = os.environ.get('HOST', '127.0.0.1')

def db_connection():
    db = "dbname='tingr' user=" + user + " host=" + host + " password =" + password
    conn = psycopg2.connect(db)

    return conn


def init_db():
    conn = db_connection()
    cur = conn.cursor()
    
    with open ('db_setup.sql','r') as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()

    with open ("../res/test.csv",'r') as f:
        read = csv.DictReader(f)
        for row in read:
            cur.execute("insert into politiker (name,party,wing) values (%s,%s,%s)", (row['x'],row['y'],row['z']))
    conn.commit()  



    conn.close()