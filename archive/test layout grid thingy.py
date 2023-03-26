# ----------- setup and imports -----------

import dash 
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template

import cufflinks as cf

import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import numpy as np

# ----------- initialise app -----------

app = Dash(__name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], 
    external_stylesheets=[dbc.themes.MORPH, dbc.icons.FONT_AWESOME],
)
load_figure_template("MORPH")
app.title = "F1 Driver Stats"
server = app.server

# ----------- app layout -----------

app.layout = dbc.Container(
    id = "root",
    children = [
        html.Div([html.H1("Formula One Driver Dashboard"), 
        html.H4("no_gutters = False"), 

        dbc.Row([
            dbc.Col(html.Div(dbc.Alert("Driver Filter")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=6)
        ]), 
  
        dbc.Row([
            dbc.Col(html.Div(dbc.Alert("Year Filter")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=6)
        ]),

        dbc.Row([
            dbc.Col(html.Div(dbc.Alert("Year Filter")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=6)
        ]),
        
        dbc.Row([
            dbc.Col(html.Div(dbc.Alert("Year Filter")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=2),
            dbc.Col(html.Div(dbc.Alert("One of two columns")), width=6)
        ]),

])])
# ----------- callbacks -----------

# ----------- run server -----------

if __name__ == "__main__":
    app.run_server(debug=True)