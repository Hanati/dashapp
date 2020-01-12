import dash
import requests
import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import time
import dash_table

def get_stock(symbol,interval):
    #proxies={"http":"clientproxy.basf.net:8080","https":"clientproxy.basf.net:8080"}
    proxies={}
    api_url = 'http://localhost:8000/stock/get'
    req_url = '/'.join([api_url, symbol, interval])
    response = requests.get(req_url, verify=False, proxies=proxies)
    return response.json()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='M0'),
    html.Div([
        html.Div([
            #dcc.Input(id='stock-abv', type='text')
            dcc.Dropdown(
                id='stock-abv',
                options=[
                    {'label': 'BASF', 'value': 'FRA:BAS',},
                    {'label': 'BAYER', 'value': 'FRA:BAYN'},
                    {'label': 'BMW', 'value': 'FRA:BMW'},
                    {'label': 'Audi', 'value': 'FRA:NSU'},
                    {'label': 'Daimler AG','value':'FRA:DAI'}
                ]),
        ],style={'width':'30%','display':'table-cell',}),
        html.Div([
            html.Button(id='submit-button', n_clicks=0, children='Show Data')
        ],style={'witdh':'5%','display':'table-cell'}),
        html.Div([
            html.Button(id='update-stock',n_clicks=0,children='Update Data')
        ],style={'witdh':'5%','display':'table-cell'}),
    ],style={'width':'40%','display':'table'}),
    html.Div([
        dcc.ConfirmDialog(
            id='confirm-success',
            message='Data successfully inserted',
        )
    ]),
    html.Hr(),
    html.Div([
        dcc.Graph(
            id='stock-graph-intra',
            figure={}),
        dcc.Graph(
            id='stock-graph-intra-vol',
            figure={})
        ],
        style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(
            id='stock-graph-daily',
            figure={}),
        dcc.Graph(
            id='stock-graph-daily-vol',
            figure={})    
        ],
        style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(
            id='stock-graph-weekly',
            figure={}
        ),
        dcc.Graph(
            id='stock-graph-weekly-vol',
            figure={}
        )],
        style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(
            id='stock-graph-monthly',
            figure={}
        ),
        dcc.Graph(
            id='stock-graph-monthly-vol',
            figure={}
        )],
        style={'width': '49%', 'display': 'inline-block'})
])

@app.callback(
    [Output('stock-graph-intra', 'figure'),
     Output('stock-graph-intra-vol', 'figure'),
     Output('stock-graph-daily', 'figure'),
     Output('stock-graph-daily-vol', 'figure'),
     Output('stock-graph-weekly','figure'),
     Output('stock-graph-weekly-vol','figure'),
     Output('stock-graph-monthly','figure'),
     Output('stock-graph-monthly-vol','figure')
    ],
    [Input('submit-button', 'n_clicks')],
    [State('stock-abv','value')]
)
def update_graph(n_clicks, input_value):
    if n_clicks==0:
        return [{},{},{},{},{},{},{},{}]
    
    intervals={'Intraday':'TIME_SERIES_INTRADAY',
            'Last 100 days':'TIME_SERIES_DAILY',
            'Last 20 years in Week':'TIME_SERIES_WEEKLY',
            'Last 20 years in Month':'TIME_SERIES_MONTHLY'}

    figures=[]
    for title,interval in intervals.items():
        data_json=get_stock(input_value,interval)
        data_df=pd.DataFrame.from_records(data_json,columns=["date","open","high","low","close","volume"])
    
        traces=[]
        for coln in data_df.columns[1:-1]:
            if title=='Intraday':
                x=list(data_df.index)
            else:
                x=list(data_df['date'])
            traces.append(dict(
                mode='lines',
                y=list(data_df[coln]),
                x=x,
                name=coln
            ))
    
        figure={
            'data': traces,
            'layout': dict(
                title=title,
                xaxis={'title': 'Date'},
                yaxis={'title': 'Value'}
                )
            }
        figure_vol={
            'data':[dict(type='bar',x=x,y=list(data_df["volume"]))],
            'layout':dict(
                xaxis={'type':'Date'},
                yaxis={'title':'Volume'}
            )
        }
        figures.append(figure)
        figures.append(figure_vol)
    return figures

@app.callback(
    Output('confirm-success', 'displayed'),
    [Input('update-stock', 'n_clicks')],
    [State('stock-abv','value')]
)
def display_confirm(n_clicks,input_value):
    intervals={'Intraday':'TIME_SERIES_INTRADAY',
            'Last 100 days':'TIME_SERIES_DAILY',
            'Last 20 years in Week':'TIME_SERIES_WEEKLY',
            'Last 20 years in Month':'TIME_SERIES_MONTHLY'}
    if n_clicks>0:
        api_url = 'http://localhost:8000/stock/post'
        for title, interval in intervals.items():
            req_url = '/'.join([api_url, input_value, interval])
            response = requests.post(req_url, verify=False)
        return True
    return False


if __name__ == '__main__':
    app.run_server(debug=True)