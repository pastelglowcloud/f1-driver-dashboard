# Set up

import dash 
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

import cufflinks as cf

import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import numpy as np

# Initialise the App

app = dash.Dash(__name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], 
    external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME]
)
app.title = "F1 Driver Stats"
server = app.server

# Data

df = pd.read_csv('races.csv')
DEFAULT_COLORSCALE = ["#f2fffb", "#bbffeb", "#98ffe0", "#79ffd6", "#6df0c8", "#69e7c0", "#59dab2","#45d0a5", "#31c194", "#2bb489", "#25a27b", "#1e906d", "#188463", "#157658", "#11684d", "#10523e"]
DEFAULT_OPACITY = 0.8
gp_options = [i for i in df['GP'].unique()]
year_options = [i for i in df['Year'].unique()]
driver_options = [i for i in df['LastName'].unique()]
location_options = [i for i in df['Location'].unique()]
#circuit_options = [i for i in df['Circuit'].unique()]
team_options = [i for i in df['TeamName'].unique()]

# App Layout

app.layout = html.Div(
    id="root",
    children = 
    [
        html.Div(
            id = 'header',
            children = [                
                html.P(
                    id="description",
                    children="Lorem Ipsim"),
                    ]
        ), 
        html.Div(
            id='filters',
            children = [
                html.P("Data Type:"),
                dcc.Dropdown(id='data_type',
                    options=['ResultType', 'QualiStatus'],
                    value='ResultType', clearable=False
                ),
                html.P("Pick a Driver:"),
                dcc.Dropdown(id='drivers',
                    options=driver_options,
                    value='Sainz', clearable=False),

                html.P("Pick a Season:"),
                dcc.Dropdown(id='year',
                    options=year_options,
                    value=2021, clearable=False)
            ]
        ),
        html.Div(
            id='bar-container',
            children = [
            html.H4('Driver Performance - Career Stats'),
            dcc.Graph(id="bar-graph"),    
            ]),
        html.Div(
            id='pie-container',
            children = [
                html.H4('Driver Performance this Year'),
                dcc.Graph(id="pie-chart"),
                html.P("Data to View:"),
                dcc.Dropdown(id='values',
                    options=['Points','Position'],
                    value='Points', clearable=False
                ),
            ]),
        html.Div
        ( id = 'scatter-container',
        children = 
        [
            html.H4('Correlation between Grid Position and Race Performance'),
            dcc.Graph(id='scatter-chart')
        ]
        )
    ]
)

@app.callback(
    Output("bar-graph", "figure"), 
    Input("data_type", "value"),
    Input("drivers", "value"),
    )
def generate_bar_chart(data_type, drivers):
    filtered_df = df[df.LastName == drivers]
    # gp_count = filtered_df[data_type].value_counts()
    fig = px.bar(filtered_df, x = "Year", y= data_type)

@app.callback(
    Output("pie-chart", "figure"), 
    Input("data_type", "value"), 
    Input("drivers", "value"),
    Input("values", "value"),
    Input("year", "value"))

def generate_pie_chart(data_type, drivers, values, year):
    filtered_df = df[df.LastName == drivers]
    filtered_df = df[df.Year == year]
    # df.groupby(values).count().reset_index()
    gp_count = filtered_df[values].value_counts()
    fig = px.pie(filtered_df, values=values, names = data_type)
    
    # fig.update_layout(
    #     title_text=values,
    #     title_x=0.5,
    #     margin=dict(b=25, t=75, l=35, r=25),
    #     height=325,
    # )
    return fig

@app.callback(
    Output("scatter-chart", "figure"), 
    Input("year", "value"), 
    Input("drivers", "value"))

def generate_scatter(year, drivers):
    filtered_df = df[df.Year == year]
    filtered_df = filtered_df[filtered_df.LastName == drivers]
    fig = px.scatter(filtered_df, x="GridPosition", y="Position",
                     size="Points", color="TeamName", hover_name="GP",
                     log_x=True, size_max=55)
    fig.update_layout(transition_duration=500)
    return fig


# @app.callback(
#     Output("graph", "figure"), 
#     Input("data_type", "value"), 
#     Input("values", "value"))
# def generate_chart(data_type, values):
#     df = px.data.tips() # replace with your own data source
#     fig = px.pie(df, values=values, data_type=data_type, hole=.3)
#     return fig


if __name__ == "__main__":
    app.run_server(debug=True)