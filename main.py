import dash
import requests
import json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import time
import os
from single import single_layout, callback_update_graph, callback_display_confirm


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Tabs(id='tabs',children=[
        dcc.Tab(label='Single', children=[single_layout]),
    ]),
])

callback_update_graph(app)
callback_display_confirm(app)


if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port='8050')
