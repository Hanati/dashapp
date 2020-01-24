from fastapi import FastAPI
import pandas as  pd
import requests
from utils_db import init_conn,insert_to_db, get_data_db
from datetime import date, timedelta

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

## read the stock, and write a postgres
@app.post("/stock/post/{stock_abv}/{stock_function}/{alpha_key}")
def update_stock(stock_abv: str,stock_function: str, alpha_key: str):
    ## get data
    proxies = {}
    api_url = 'https://www.alphavantage.co/query?function='+ stock_function
    if stock_function=='TIME_SERIES_INTRADAY':
        api_url=api_url+'&interval=5min'
    req_url = ''.join([api_url, '&symbol=', stock_abv, '&apikey=', alpha_key])
    response = requests.get(req_url, verify=False, proxies=proxies)
    data=response.json()

    ## json to dataframe
    df= pd.DataFrame.from_dict(data[list(data.keys())[1]]).transpose()
    df = df.apply(pd.to_numeric)
    df=df[::-1]
    df.columns=['open','high','low','close','volume']
    df['date']=df.index
    df['date']=df['date'].apply(lambda x: x.split(' ')[0])

    ## insert into db
    p_conn=init_conn()
    table_name='_'.join([stock_abv.replace(':','_'),stock_function]).lower()
    message=insert_to_db(p_conn,table_name,df)
 
    return message

## read from postgres
@app.get("/stock/get/{stock_abv}/{stock_function}")
def get_stock(stock_abv:str, stock_function: str):
    p_conn=init_conn()
    results=get_data_db(p_conn,stock_abv,stock_function)
    return results

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
