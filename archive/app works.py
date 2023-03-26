# --------------------------------------------- setup and imports ---------------------------------------------

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template
import dash_daq as daq

import cufflinks as cf

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"
load_figure_template("DARKLY")

import pandas as pd

# --------------------------------------------- initialise app ---------------------------------------------

app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], 
            title = "F1 Driver Stats", update_title='Enabling DRS...', 
            external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME])
server = app.server

# --------------------------------------------- define data ---------------------------------------------

df = pd.read_csv('data/races.csv')
drivers = pd.read_csv('data/drivers.csv')
df["EventDate"] = pd.to_datetime(df["EventDate"]) #move to data?
df["EventDate"] = df["EventDate"].dt.date #move to data?
df = df.sort_values(by=['EventDate']) #move to data?

year_options = sorted([i for i in df['Year'].unique()])
driver_options = sorted([i for i in drivers['FullName'].unique()])

# --------------------------------------------- build components ---------------------------------------------

my_title = dcc.Markdown("# Learn about your favourite drivers!")
driver_dropdown = dcc.Dropdown(id = 'chosen_driver', options = driver_options, value= "Carlos Sainz", clearable = False)
year_dropdown = dcc.Dropdown(id = 'chosen_year', options = year_options, value= "2021", clearable = False)
driver_card = dbc.Card([dbc.CardImg(src="assets/carlos.jpg"),dbc.CardBody(html.P("Scuderia Ferrari"))])

# cards and gauges

gauge_finished_races = dbc.Card(children=[
    dbc.CardHeader("Races Finished 2018-2022"), 
    dbc.CardBody([html.Div(daq.Gauge(id="races_completed", min=0, max=100, value=0, showCurrentValue=True,color="#fec036"))])])  
gauge_races_in_points = dbc.Card(className = "gauge-one", children=[dbc.CardHeader("Races in Points 2018-2022", className="gauge-two"),dbc.CardBody([html.Div(daq.Gauge(id="races_in_points", className = "gauge_three", min=0, max=100, value=0, showCurrentValue=True,color= "#fec036" ), className="gauge-four")], className="gauge-flex")])

kpi_career_points = dcc.Graph(id="total_career_points_card", className = "kpi-card")
kpi_season_points = dcc.Graph(id="total_season_points_card", className = "kpi-card")
kpi_highest_position = dcc.Graph(id="highest_position", className = "kpi-card")
kpi_total_wins = dcc.Graph(id="total_wins", className = "kpi-card")

# pie chart

pie_success = dcc.Graph(id="driver_success", className="pie-chart")
pie_dnf = dcc.Graph(id="dnf_reason", className="pie-chart")

# twitter

twitter_feed = html.Iframe(srcDoc=''' <a class="twitter-timeline" data-theme="dark" href="https://twitter.com/Carlossainz55?s=20&t=ZfIXlnPbSTRXuUH4zkhUQA"> Tweets by Carlos Sainz </a> 
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>''', height=800, width=300)

# graphs 

graph_overall_progress = dcc.Graph(id="overall_progression", className="graph")
graph_season_progress = dcc.Graph(id="season_progression", className="graph")
graph_avg_points = dcc.Graph(id="bar_points_avg", className="graph")
graph_total_points = dcc.Graph(id="bar_points_total", className="graph")
graph_position_scatter = dcc.Graph(id="scatter", className="graph")

table = dbc.Col(dash_table.DataTable(id="table-container"))

# --------------------------------------------- app layout ---------------------------------------------

app.layout = dbc.Container(id = "root",

    children = [

        dbc.Row([dbc.Col(id = "header", children = [html.H1("F1 Driver Dashboard")]),]),

        dbc.Row([
            dbc.Col(className = "filters", children = [driver_dropdown]),
            dbc.Col(className = "filters", children = [year_dropdown])], className="meow"),

        dbc.Row(
            
            [dbc.Col(id = "section1", width = 3, children = [ 
            dbc.Row(driver_card),
            dbc.Row([twitter_feed])]),

            dbc.Col(id = "section2", width = 3, children = [
                dbc.Row([dbc.Col(kpi_career_points)]), 
                dbc.Row([dbc.Col(kpi_season_points)]), 
                dbc.Row([dbc.Col(kpi_highest_position)]), 
                dbc.Row([dbc.Col(kpi_total_wins)]), 
                dbc.Row([dbc.Col(pie_success)]),
                dbc.Row([dbc.Col(pie_dnf)]),
                # dbc.Row([dbc.Col(gauge_finished_races)]), 
                # dbc.Row([dbc.Col(gauge_races_in_points)]),
            ]),

            dbc.Col(id = "section3", width=6, children = [
                dbc.Row(graph_overall_progress), 
                dbc.Row(graph_season_progress),
                dbc.Row(graph_avg_points),
                dbc.Row(graph_total_points),
                dbc.Row(graph_position_scatter)
            ]),
        ]),
        dbc.Row([table])
    ])

# ----------------------------------------------- TABLE CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("table-container", "data"), 
    Input("chosen_year","value"), 
    Input("chosen_driver","value"),
)
def display_table(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    season_summary = driver_year_df[['RoundNumber', 'EventDate', 'GP', 'EventFormat', 'Location', 'Country', 'QualiStatus', 'GridPosition','ResultType', 'Status','Position', 'Points']]
    return season_summary.to_dict("records")

        
# ----------------------------------------------- BAR CALLBACKS -------------------------------------------------- #

@app.callback(Output("bar_points_avg", "figure"), Input("chosen_driver","value"))
def fig_avg_bar_pts(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_yr_summary = driver_df.groupby('Year').agg(TotalPoints = pd.NamedAgg(column="Points", aggfunc=sum), TeamName = pd.NamedAgg(column="TeamName", aggfunc=max), TotalRaces = pd.NamedAgg(column="Counter", aggfunc=sum)).reset_index()
    driver_yr_summary["AveragePoints"] = driver_yr_summary.TotalPoints / driver_yr_summary.TotalRaces
    fig = px.bar(driver_yr_summary, x='Year', y='AveragePoints', title=f'Average Points by Season - {chosen_driver}', labels = {'Points':'Points', 'Year':'Season'}, color = "TeamName", text_auto=True, opacity=0.9)
    fig.update_xaxes(type='category')
    return fig

@app.callback(Output("bar_points_total", "figure"), Input("chosen_driver","value"))
def fig_total_bar_pts(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = px.bar(driver_df, x='Year', y='Points', title=f'Points by Season - {chosen_driver}', labels = {'Points':'Points', 'Year':'Season'}, color='TeamName',text_auto=True, opacity=0.9)
    fig.update_xaxes(type='category')
    return fig

# ----------------------------------------------- LINE & AREA CALLBACKS -------------------------------------------------- #

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

# ----------------------------------------------- SCATTER CALLBACKS -------------------------------------------------- #

@app.callback(Output("scatter", "figure"), Input("chosen_driver","value"),)
def fig_scatter(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = px.scatter(data_frame = driver_df, x = "GridPosition", y = "Position", range_x = [0,20], range_y = [0,25], color = "Year", trendline="ols", trendline_scope= "overall")
    return fig

# ----------------------------------------------- PIE CALLBACKS -------------------------------------------------- #

@app.callback(Output("driver_success", "figure"), Input("chosen_driver","value"),)
def pie_driver_success(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = px.pie(driver_df, values='Counter', names='ResultType', title=f'Race Results for Career - {chosen_driver}')
    return fig

@app.callback(Output("dnf_reason", "figure"), Input("chosen_driver","value"),)
def pie_dnf_reason(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_df_dnf = driver_df.query("Status != 'Finished'").query("Status != '+1 Lap'").query("Status != '+2 Laps'")
    fig = px.pie(data_frame = driver_df_dnf, values ='Counter', names = 'Status', title="Most frequent cause of DNF" )
    return fig

# ----------------------------------------------- GAUGE CALLBACKS -------------------------------------------------- #

# @app.callback(Output("races_completed", "value"), Input("chosen_driver","value"))
# def update_output(chosen_driver):
#     driver_df = df.loc[df['FullName'] == chosen_driver]
#     category_races = driver_df[["Status", "Counter"]].groupby("Status").sum().reset_index()
#     sum_completed = category_races["Status"== "Finished"]["Counter"][0]
#     data_races_completed = ((sum_completed)/(driver_df["Counter"].sum()))
#     pct_completed = round(data_races_completed*100, ndigits=2)
#     return pct_completed

# @app.callback(Output("races_in_points", "value"), Input("chosen_driver","value"))
# def fig_races_in_points(chosen_driver):
#     chart_category = "ResultType"
#     driver_df = df.loc[df['FullName'] == chosen_driver]
#     category_races = driver_df[[chart_category, "Counter"]].groupby(chart_category).sum().reset_index()
#     data_races_in_points = ((category_races[category_races[chart_category]!= "NoPoints"]["Counter"][0])/(category_races["Counter"].sum()))
#     pct_points = round(data_races_in_points*100, ndigits=2)
#     return pct_points

# ----------------------------------------------- CARD CALLBACKS -------------------------------------------------- #

@app.callback(Output("total_career_points_card", "figure"), Input("chosen_driver","value"))
def total_career_points_card(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = go.Figure(go.Indicator(mode = "number",value = driver_df["Points"].sum(), title = {'text': f"Total Points 2018-2022"}, domain = {'x': [0,1], 'y': [0,1]}))
    fig.update_layout(height=200)
    return fig

@app.callback(Output("total_season_points_card", "figure"), Input("chosen_year","value"), Input("chosen_driver","value"))
def total_season_points_card(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    fig = go.Figure(go.Indicator(mode = "number",value = driver_year_df["Points"].sum(), title = {'text': f"Total Points for {chosen_year} season"}, domain = {'x': [0,1], 'y': [0,1]}))
    fig.update_layout(height=200)
    return fig

@app.callback(Output("total_wins", "figure"), Input("chosen_driver","value"))
def total_wins_card(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = go.Figure(go.Indicator(mode = "number" ,value = driver_df.query("Position == 1").sum()["Counter"], title = {'text': "Number of Wins 2018-2022"}, domain = {'x': [0,1], 'y': [0,1]}))
    fig.update_layout(height=200)
    return fig

@app.callback(Output("highest_position", "figure"), Input("chosen_driver","value"))
def card_highest_position(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = go.Figure(go.Indicator(mode = "number", value = driver_df["Position"].min(), title = {'text': "Highest Race Position 2018-2022"}, domain = {'x': [0,1], 'y': [0,1]}))
    fig.update_layout(height=200)
    return fig

# --------------------------------------------- run server ---------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True)