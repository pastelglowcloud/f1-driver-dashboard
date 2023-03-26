# Set up

import dash 
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, dcc, html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import cufflinks as cf
import plotly.graph_objects as go

import os
import pathlib
import re
import pandas as pd

# Initialise the App

app = dash.Dash(__name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], 
    external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME]
)
app.title = "US Opioid Epidemic"
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
    id='root',
    children = [
        html.Div(
            id="header",
            children=[
                html.P(
                    id="description",
                    children="† Deaths are classified using the International Classification of Diseases,Tenth Revision (ICD–10). Drug-poisoning deaths are defined as having ICD–10 underlyingcodes (unintentional), X60–X64 (suicide), X85 (homicide), or Y10–Y14 (undetermined intent)."
                ),
            ],
        ),
                html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(id="years-slider", min=2018, max=2022, value=2022,marks={str(year): {"label": str(year), "style": {"color": "#7fafdf"},}for year in [2018,2019, 2020, 2021, 2022]},),
                            ],
                        ),
                        html.Div(
                            id="piechart-container",
                            children=[
                                html.P(
                                    "Races by Result Type in {0}".format(2018),id="piechart_title",),
                                dcc.Graph(
                                    id="driver-pies")])]),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {"label": "Line Chart of total number of Points (single year)", "value": "show_season_points"},
                                {"label": "Line Chart of total number of Points (2018-2022)", "value": "show_all_time_points",},
                                {"label": "Line Chart of average race position (2018-2022)", "value": "career_position",},
                                {"label": "Scatter Chart of Grid and Race Positions","value": "show_grid_race_position",}],
                            value="show_all_time_points", id="chart-dropdown",),

                        dcc.Graph(id="selected-data", figure=dict(data=[dict(x=0, y=0)], layout=dict(paper_bgcolor="#F4F4F8", plot_bgcolor="#F4F4F8", autofill=True, margin=dict(t=75, r=50, b=100, l=50)
                        ),),),],),
                    ],), ],)


@app.callback(Output("piechart_title", "children"), [Input("years-slider", "value")])
def update_pie_title(year):
    return f"Races by Result Type in {year}"

@app.callback(Output("selected-data", "figure"), 
    [
        Input('driver-pies', 'selectedData'),
        Input('chart-dropdown', 'value'),
        Input('years-slider', 'value')
    ])
def display_selected_data(selectedData, chart_dropdown, year):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select counties",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    if chart_dropdown != 'show_all_time_points':
        title = "Points per Season"
        AGGREGATE_BY = "Points"
        if "show_season_points" == chart_dropdown:
            dff = df[df.Year == year]
            title = "Points Gained per Season, <b>{0}</b>".format(year)
        elif "career_position" == chart_dropdown:
            dff = df[df.Year == year]
            title = "Average Position by Season, <b>{0}</b>".format(year)
            AGGREGATE_BY = "Position"
        dff[AGGREGATE_BY] = pd.to_numeric(df[AGGREGATE_BY], errors="coerce")
        driver_perfs = dff.groupby("LastName")[AGGREGATE_BY].average()
        driver_perfs = driver_perfs.sort_values()
        # Only look at non-zero rows:
        driver_perfs = driver_perfs[driver_perfs > 0]
        fig = driver_perfs.iplot(
            kind="bar", y=AGGREGATE_BY, title=title, asFigure=True
        )

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_data[0]["text"] = driver_perfs.values.tolist()
        fig_data[0]["marker"]["color"] = "#2cfec1"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#1f2630"
        fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#2cfec1"
        fig_layout["title"]["font"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig

    fig = dff.iplot(
        kind="area",
        x="Year",
        y="Positions",
        text="Positions",
        categories="LastName",
        colors=[
            "#1b9e77",
            "#d95f02",
            "#7570b3",
            "#e7298a",
            "#66a61e",
            "#e6ab02",
            "#a6761d",
            "#666666",
            "#1b9e77",
        ],
        vline=[year],
        asFigure=True,
    )
    for i, trace in enumerate(fig["data"]):
        trace["mode"] = "lines+markers"
        trace["marker"]["size"] = 4
        trace["marker"]["line"]["width"] = 1
        trace["type"] = "scatter"
        for prop in trace:
            fig["data"][i][prop] = trace[prop]

    # Only show first 500 lines
    fig["data"] = fig["data"][0:500]

    fig_layout = fig["layout"]

    # See plot.ly/python/reference
    fig_layout["yaxis"]["title"] = "Age-adjusted death rate per county per year"
    fig_layout["xaxis"]["title"] = ""
    fig_layout["yaxis"]["fixedrange"] = True
    fig_layout["xaxis"]["fixedrange"] = False
    fig_layout["hovermode"] = "closest"
    fig_layout["title"] = "<b>{0}</b> counties selected"
    fig_layout["legend"] = dict(orientation="v")
    fig_layout["autosize"] = True
    fig_layout["paper_bgcolor"] = "#1f2630"
    fig_layout["plot_bgcolor"] = "#1f2630"
    fig_layout["font"]["color"] = "#2cfec1"
    fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
    fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)

# app.layout = html.Div([
#     html.H4('Driver Performance - Career Stats'),
#     dcc.Graph(id="graph"),
#     html.P("Data Type:"),
#     dcc.Dropdown(id='names',
#         options=['ResultType', 'QualiStatus'],
#         value='ResultType', clearable=False
#     ),
#     html.P("Pick a Driver:"),
#     dcc.Dropdown(id='drivers',
#         options=driver_options,
#         value='Sainz', clearable=False),
# ])

# @app.callback(
#     Output("graph", "figure"), 
#     Input("names", "value"),
#     Input("drivers", "value"),
#     )

# def generate_pie_chart(names, drivers):
#     filtered_df = df[df.LastName == drivers]
#     df.groupby(names).count().reset_index()
#     gp_count = filtered_df[names].value_counts()
#     fig = px.pie(filtered_df, values=gp_count, names= names)
#     return fig

# # app.layout = html.Div([
# #     html.H4('Driver Performance this Year'),
# #     dcc.Graph(id="graph"),
# #     html.P("Data Type:"),
# #     dcc.Dropdown(id='names',
# #         options=['ResultType', 'QualiType'],
# #         value='ResultType', clearable=False
# #     ),
# #     html.P("Data to View:"),
# #     dcc.Dropdown(id='values',
# #         options=['Points','Position'],
# #         value='Points', clearable=False
# #     ),
# # ])

# # @app.callback(
# #     Output("graph", "figure"), 
# #     Input("names", "value"), 
# #     Input("values", "value"))


# # def generate_scatter(selected_year, selected_driver):
# #     filtered_df = df[df.Year == selected_year]
# #     fig = px.scatter(filtered_df, x="GridPosition", y="Position",
# #                      size="Points", color="TeamName", hover_name="GP",
# #                      log_x=True, size_max=55)
# #     fig.update_layout(transition_duration=500)
# #     return fig


# # def generate_chart(names, values):
# #     fig = go.Figure(
# #         data=[
# #             go.Pie(
# #                 labels=values,
# #                 values= df.loc[df['LastName'] == names],
# #                 textinfo="label+percent",
# #                 textposition="inside",
# #                 sort=False,
# #                 hoverinfo="none",
# #             )
# #         ]
# #     )
# #     fig.update_layout(
# #         title_text=values,
# #         title_x=0.5,
# #         margin=dict(b=25, t=75, l=35, r=25),
# #         height=325,
# #     )
# #     return fig

# # from dash import Dash, dcc, html, Input, Output
# # import plotly.express as px

# # app = Dash(__name__)


# # app.layout = html.Div([
# #     html.H4('Analysis of the restaurant sales'),
# #     dcc.Graph(id="graph"),
# #     html.P("Names:"),
# #     dcc.Dropdown(id='names',
# #         options=['smoker', 'day', 'time', 'sex'],
# #         value='day', clearable=False
# #     ),
# #     html.P("Values:"),
# #     dcc.Dropdown(id='values',
# #         options=['total_bill', 'tip', 'size'],
# #         value='total_bill', clearable=False
# #     ),
# # ])


# # @app.callback(
# #     Output("graph", "figure"), 
# #     Input("names", "value"), 
# #     Input("values", "value"))
# # def generate_chart(names, values):
# #     df = px.data.tips() # replace with your own data source
# #     fig = px.pie(df, values=values, names=names, hole=.3)
# #     return fig


# app.run_server(debug=True)