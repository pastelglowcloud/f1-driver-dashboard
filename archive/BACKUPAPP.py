# ----------- setup and imports -----------

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template
import dash_daq as daq
import cufflinks as cf

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"

import pandas as pd
import numpy as np

# ----------- initialise app -----------

app = Dash(__name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], 
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME])
load_figure_template("DARKLY")
app.title = "F1 Driver Stats"
server = app.server

# ----------- define data -----------

df = pd.read_csv('races.csv')
df["EventDate"] = pd.to_datetime(df["EventDate"])
df["EventDate"] = df["EventDate"].dt.date
df = df.sort_values(by=['EventDate'])

year_options = [i for i in df['Year'].unique()]
driver_options = [i for i in df['FullName'].unique()]

# ----------- build components -----------

my_title = dcc.Markdown("# Learn about your favourite drivers!")
driver_dropdown = dcc.Dropdown(id = 'chosen_driver', options = driver_options, value= "Carlos Sainz", clearable = False)
year_dropdown = dcc.Dropdown(id = 'chosen_year', options = year_options, value= "2022", clearable = False)
def logo(app):
    title = html.H5(
        "PREDICTIVE MAINTENANCE DASHBOARD FOR WIND TURBINES",
        style={"marginTop": 5, "marginLeft": "10px"})
    info_about_app = html.H6(
        "This Dashboard is focused on estimating the Remaining Useful Life (RUL) in wind turbines via Machine Learning."
        " RUL is defined as the time until the next fault and estimated via XGBoost algorithm.",
        style={"marginLeft": "10px"})
    logo_image = html.Img(
        src=app.get_asset_url("assets/racing-car.png"), style={"float": "right", "height": 50})
    link = html.A(logo_image, href="https://plotly.com/dash/")
    return dbc.Row(
        [dbc.Col([dbc.Row([title]), dbc.Row([info_about_app])]), dbc.Col(link)]
    )



# ----------- app layout -----------

app.layout = dbc.Container(id = "root",
    children = 
    [
        html.Div(id = "header", children = [my_title]),
        html.Div(id = "section1", children = [
            dbc.Row([
                dbc.Col(id="driver_filter", children = [html.P("Pick a Driver:"), driver_dropdown], width=6),
                dbc.Col(id="year_filter", children = [html.P("Pick a Season:"), year_dropdown], width=6)
            ]), 
            dbc.Row(dbc.Card([dbc.CardImg(src="assets/carlos.jpg"),dbc.CardBody(html.P("Scuderia Ferrari"))])),
        ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div(id = "section2", children = [
            dbc.Row([dbc.Col(dcc.Graph(id="total_career_points_card")),]), 
            dbc.Row([dbc.Col(dcc.Graph(id="total_season_points_card")),]), 
            dbc.Row([dbc.Col(dcc.Graph(id="highest_position"))]), 
        ], style={'width': '20%', 'display': 'inline-block'}),

        html.Div(id = "section3", children = [
            dbc.Row(dcc.Graph(id="overall_progression")), 
            dbc.Row(dcc.Graph(id="season_progression")),
            dbc.Row(dcc.Graph(id="bar_points_avg")),
            dbc.Row(dcc.Graph(id="scatter"))
        ],style={'width': '40%', 'display': 'inline-block'}),
    ]
)

# ------------- BAR CALLBACKS ---------------- #

@app.callback(Output("bar_points_avg", "figure"), Input("chosen_driver","value"))
def fig_avg_bar_pts(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_yr_summary = driver_df.groupby('Year').agg(TotalPoints = pd.NamedAgg(column="Points", aggfunc=sum), TeamName = pd.NamedAgg(column="TeamName", aggfunc=max), TotalRaces = pd.NamedAgg(column="Counter", aggfunc=sum)).reset_index()
    driver_yr_summary["AveragePoints"] = driver_yr_summary.TotalPoints / driver_yr_summary.TotalRaces
    fig = px.bar(driver_yr_summary, x='Year', y='AveragePoints', title=f'Average Points by Season - {chosen_driver}', labels = {'Points':'Points', 'Year':'Season'}, color = "TeamName", text_auto=True, opacity=0.9)
    fig.update_xaxes(type='category')
    return fig

# ------------- LINE CALLBACKS ---------------- #

@app.callback(Output("overall_progression", "figure"), Input("chosen_driver","value"))
def card_overall_progression(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = px.line(data_frame=driver_df, x="EventDate", y=["Position", "GridPosition"], range_y = [0,20],  title="Overview 2018-2022")
    return fig

@app.callback(Output("season_progression", "figure"), Input("chosen_year","value"), Input("chosen_driver","value"),)
def fig_season_progression(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    fig = px.area(data_frame=driver_year_df, x="EventDate", y=["Position", "GridPosition"], range_y = [0,20], title=f"Overview of {chosen_year} Season")
    return fig

# ------------- SCATTER CALLBACKS ---------------- #

@app.callback(Output("scatter", "figure"), Input("chosen_driver","value"),)
def fig_scatter(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = px.scatter(data_frame = driver_df, x = "GridPosition", y = "Position", range_x = [0,20], range_y = [0,20], color = "Year", trendline="ols", trendline_scope= "overall")
    return fig

# ------------- PIE CALLBACKS ---------------- #

# ------------- GAUGE CALLBACKS ---------------- #

# ------------- CARD CALLBACKS ---------------- #

@app.callback(Output("total_career_points_card", "figure"), Input("chosen_driver","value"))
def total_career_points_card(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = go.Figure(go.Indicator(mode = "number", value = driver_df.query("Position == 1").sum()["Counter"], title = {'text': "Number of Wins 2018-2022"}, domain = {'x': [0,1], 'y': [0,1]}))
    return fig

@app.callback(Output("total_season_points_card", "figure"), Input("chosen_year","value"), Input("chosen_driver","value"))
def total_season_points_card(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    fig = go.Figure(go.Indicator(mode = "number",value = driver_year_df["Points"].sum(), title = {'text': f"Total Points for {chosen_year} season"}, domain = {'x': [0,1], 'y': [0,1]}))
    return fig

@app.callback(Output("highest_position", "figure"), Input("chosen_driver","value"))
def card_highest_position(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = go.Figure(go.Indicator(mode = "number", value = driver_df["Position"].min(), title = {'text': "Highest Race Position 2018-2022"}, domain = {'x': [0,1], 'y': [0,1]}))
    return fig

# ----------- run server -----------

if __name__ == "__main__":
    app.run_server(debug=True)