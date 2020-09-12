#import psycopg2
#from psycopg2.extras import execute_batch
import pg8000
import numpy as np
import pandas as pd
from datetime import date,timedelta

def init_conn():
    p_conn=pg8000.connect(
        host='db',
        port=5432,
        user='postgres',
        password='postgres')
    return p_conn

def last_entry(p_conn,tablename):
    cur=p_conn.cursor()
    cur.execute("select max(date) from "+tablename)
    max_date=cur.fetchall()
    cur.close()
    
    return str(max_date[0][0])

def create_tb(p_conn,tablename):
    cur = p_conn.cursor()
    cur.execute("select * from information_schema.tables where table_name=%s", (tablename,))
    table_count=cur.rowcount
    if table_count==0:
        create_template=('''CREATE TABLE IF NOT EXISTS {table_name} 
                (date Date NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INT NOT NULL)''')
        table_query=create_template.format(table_name=tablename)
        cur = p_conn.cursor()
        cur.execute(table_query)
        #p_conn.commit()
        cur.close()
        return table_count
    table_count+=1
    return table_count

def insert_to_db(p_conn,tablename,df):
    ll=create_tb(p_conn,tablename)
    if ll!=0:
        last_date=last_entry(p_conn,tablename)
        idx=np.where(df['date']>str(last_date))[0]
        df=df.iloc[idx]
    if len(df)==0:
        return '0 records written'
    df_columns = list(df)
    # create (col1,col2,...)
    columns = ",".join(df_columns)

    # create VALUES('%s', '%s",...) one '%s' per column
    values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

    #create INSERT INTO table (columns) VALUES('%s',...)
    insert_stmt = "INSERT INTO {} ({}) {}".format(tablename,columns,values)

    cur =p_conn.cursor()
    cur.executemany(insert_stmt, df.values)
    p_conn.commit()
    cur.close()

    return str(len(df))+' records written,'+str(ll)+tablename

def get_data_db(p_conn, stock_abv, stock_function):
    table_name='_'.join([stock_abv.replace(':','_'),stock_function]).lower()

    if stock_function=="TIME_SERIES_INTRADAY":
        yes_date=date.today()-timedelta(1)
        query="select * from "+table_name+" where date = '"+str(yes_date)+"'"
    elif stock_function=="TIME_SERIES_DAILY":
        query="select * from "+table_name+" order by date DESC limit 100"
    else:
        query="select * from "+table_name
    cur = p_conn.cursor()
    cur.execute(query)
    records=cur.fetchall()
    return list(records)
