# --------------------------------------------- setup and imports ---------------------------------------------

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.templates.default = "plotly_dark"
load_figure_template("DARKLY")
import pandas as pd

# --------------------------------------------- define data ---------------------------------------------

df = pd.read_csv('data/races.csv')
drivers = pd.read_csv('data/drivers.csv')
year_options = sorted([i for i in df['Year'].unique()])
driver_options = sorted([i for i in drivers['FullName'].unique() if i not in ['Jack Aitken', 'Nyck De Vries']])

# --------------------------------------------- initialise app ---------------------------------------------

app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], 
            title = "F1 Driver Stats", update_title='Enabling DRS...', 
            external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# --------------------------------------------- build components ---------------------------------------------

driver_dropdown = dcc.Dropdown(id = "chosen_driver", options = driver_options, value= "Carlos Sainz", clearable = False, className="filter")
year_dropdown = dcc.Dropdown(id = "chosen_year", options = year_options, value= 2021, clearable = False, style={'margin-bottom': '5%'})
driver_image= dbc.CardImg(id = "driver-img", src = "assets/profiles/Carlos Sainz.png")

driver_info = dbc.CardGroup([
        dbc.Col(dbc.Card(children=[dbc.CardHeader('Nationality'), dbc.CardImg(id = "d_flag", src = "assets/flags/es.png", className="card-img-top img-fluid")]), width=4),
        dbc.Col(dbc.Card(children=[dbc.CardHeader('Number'), dbc.CardBody(id = "driver_number", children = [html.H2("55")], className="border-0 bg-transparent")]), width=4),
        dbc.Col(dbc.Card(children=[dbc.CardHeader('Team'), dbc.CardBody(id = "team_name", children = [html.H3("Ferrari")], className="border-0 bg-transparent")]), width=4),
], id="kpi_group")

twitter_feed = html.Iframe(srcDoc=''' <a class="twitter-timeline" data-theme="dark" href="https://twitter.com/Carlossainz55"> Tweets by Carlos Sainz </a> 
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>''', height=800, width=300, id = "twitter")

kpi = dbc.CardGroup([
    dbc.Card(children=[dbc.CardHeader('Points - Career'), dbc.CardBody(id="total_career_points_card")]),
    dbc.Card(children=[dbc.CardHeader('Points - Season'), dbc.CardBody(id="total_season_points_card")]),
    dbc.Card(children=[dbc.CardHeader('Highest Position'), dbc.CardBody(id="highest_position")]),
    dbc.Card(children=[dbc.CardHeader('Total Wins'),dbc.CardBody(id="total_wins")])
])

success_pie = dcc.Graph(id="card_success")
dnf_pie = dcc.Graph(id="card_dnf")

graph_overall_progress = dcc.Graph(id="overall_progression", className="graph")
graph_season_progress = dcc.Graph(id="season_progression", className="graph")
graph_avg_points = dcc.Graph(id="bar_points_avg", className="graph")
graph_total_points = dcc.Graph(id="bar_points_total", className="graph")
graph_position_scatter = dcc.Graph(id="scatter", className="graph")

table = dcc.Graph(id="table-container")

# --------------------------------------------- app layout ---------------------------------------------

app.layout = dbc.Container(id = "root",
    children = [
        dbc.Row([dbc.Col(id = "header", children = [html.H1("It's Lights Out and Away We Go!")]),]),
        dbc.Row([
            dbc.Col(driver_dropdown),
            dbc.Col(year_dropdown)
            ]),
        dbc.Row(
            [dbc.Col(id = "section1", children = [ 
                dbc.Row(driver_image),
                dbc.Row(driver_info),
                dbc.Row(twitter_feed),
                dbc.Row([success_pie, dnf_pie]),
                ]),
            dbc.Col(id = "section2", width=8, children = [
                dbc.Row(kpi),
                dbc.Row(graph_overall_progress), 
                dbc.Row(graph_season_progress),
                dbc.Row(graph_avg_points),
                dbc.Row(graph_total_points),
                dbc.Row(graph_position_scatter)
            ]),
        ]),
        dbc.Row([table])
    ])

# ----------------------------------------------- IMG AND TWITTER CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("driver-img", 'src'),
    Output("d_flag", 'src'),
    Output("twitter", 'srcDoc'),
    Input("chosen_driver","value"))
def update_driver_info(chosen_driver):
    country = drivers.loc[drivers['FullName'] == chosen_driver]["FlagURL"]
    country = country.values[0]
    driver_pic = f"assets/profiles/{chosen_driver}.png"
    driver_country = f"assets/flags/{country}.png"
    twitter_url = drivers.loc[drivers['FullName'] == chosen_driver]["twitter"]
    twitter_url = twitter_url.values[0]
    twitter_url = str('"'+twitter_url+'"')
    twitter_link = f'''<a class="twitter-timeline" data-theme="dark" href={twitter_url}> Tweets by Carlos Sainz </a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'''
    return driver_pic, driver_country, twitter_link

# ----------------------------------------------- TABLE CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("table-container", "figure"), 
    Input("chosen_year","value"), 
    Input("chosen_driver","value"))
def display_table(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    season_summary = driver_year_df[['RoundNumber', 'EventDate', 'GP', 'EventFormat', 'Location', 'QualiStatus', 'GridPosition','ResultType', 'Status', 'Position', 'Points']]
    season_summary['CumulativePoints'] = season_summary['Points'].cumsum()
    fig = go.Figure(data=[go.Table(
    header=dict(
        values=list(season_summary.columns),
        fill_color='#e45756',align='center'),
    cells=dict(
        values=[season_summary.RoundNumber, season_summary.EventDate, season_summary.GP, season_summary.EventFormat, season_summary.Location, season_summary.QualiStatus, season_summary.GridPosition, season_summary.ResultType, season_summary.Status, season_summary.Position, season_summary.Points, season_summary.CumulativePoints], 
        fill_color = 'rgba(0, 0, 0, 0)', align='center'))])
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(margin=dict(t=0, b=100, l=0, r=0, pad=0))
    fig.update_layout(title_text=f'Season Summary - {chosen_driver}', title_x=0.5)
    fig.update_layout(font_color='#f5f5dc', title_font_color='#f5f5dc')
    return fig

# ----------------------------------------------- BAR CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("bar_points_avg", "figure"), 
    Output("bar_points_total", "figure"),
    Input("chosen_driver","value"))
def fig_avg_bar_pts(chosen_driver):
    # data       
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_yr_summary = driver_df.groupby('Year').agg(TotalPoints = pd.NamedAgg(column="Points", aggfunc=sum), TeamName = pd.NamedAgg(column="TeamName", aggfunc=max), TotalRaces = pd.NamedAgg(column="Counter", aggfunc=sum)).reset_index()
    driver_yr_summary["AveragePoints"] = driver_yr_summary.TotalPoints / driver_yr_summary.TotalRaces
    # average points graph
    avg_points_figure = px.bar(driver_yr_summary, x='Year', y='AveragePoints', labels = {'Points':'Points', 'Year':'Season'}, color = "TeamName", text_auto=True, opacity=0.9, color_discrete_sequence=px.colors.qualitative.T10)
    avg_points_figure.update_xaxes(type='category')
    avg_points_figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), legend_title="")
    avg_points_figure.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    avg_points_figure.update_layout(title_text=f'Average Points by Season - {chosen_driver}', title_x=0.5)
    # total points graph
    total_points_figure = px.bar(driver_yr_summary, x='Year', y='TotalPoints', labels = {'Points':'Points', 'Year':'Season'}, color='TeamName', text_auto=True, opacity=0.9, color_discrete_sequence=px.colors.qualitative.T10)
    total_points_figure.update_xaxes(type='category')
    total_points_figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), legend_title="")
    total_points_figure.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    total_points_figure.update_layout(title_text=f'Points by Season - {chosen_driver}', title_x=0.5)
    return avg_points_figure, total_points_figure

# ----------------------------------------------- LINE & AREA CALLBACKS  -------------------------------------------------- #

@app.callback(
    Output("overall_progression", "figure"), 
    Input("chosen_driver","value"))
def card_overall_progression(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    fig = px.line(data_frame=driver_df, x="EventDate", y=["Position", "GridPosition"], range_y = [0,20], color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),hovermode="x", legend_title="",)
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(
        title={'text': 'Overview 2018-2022','y':0.9,'x':0.5}, 
        font=dict(family="Arial",size=18, color=“red”)
    )
    return fig

@app.callback(
    Output("season_progression", "figure"), 
    Input("chosen_year","value"), 
    Input("chosen_driver","value"))
def fig_season_progression(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    fig = px.line(data_frame=driver_year_df, x="EventDate", y=["Position", "GridPosition"], range_y = [0,20], color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),hovermode="x", legend_title="",)
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(title_text=f"Overview of {chosen_year} Season", title_x=0.5)
    return fig

# ----------------------------------------------- SCATTER CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("scatter", "figure"), 
    Input("chosen_driver","value"))
def fig_scatter(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_df["Year"] = driver_df["Year"].astype(str)
    fig = px.scatter(data_frame = driver_df, x = "GridPosition", y = "Position", range_x = [0,20], range_y = [0,25], color = "TeamName", trendline="ols", trendline_scope= "overall", color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), legend_title="",)
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(title_text="Correlation between Grid Position and Final Result", title_x=0.5)
    return fig

# ----------------------------------------------- PIE CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("card_success", "figure"), 
    Output("card_dnf", "figure"),
    Input("chosen_driver","value")
)
def update_pies(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_df_dnf = driver_df.query("Status != 'Finished'").query("Status != '+1 Lap'").query("Status != '+2 Laps'")
    success = px.pie(driver_df, values='Counter', names='ResultType', title=f'Race Results for Career - {chosen_driver}', color_discrete_sequence=px.colors.qualitative.T10, hole=.3)
    dnf = px.pie(data_frame = driver_df_dnf, values ='Counter', names = 'Status', title="Most frequent cause of DNF", color_discrete_sequence=px.colors.qualitative.T10, hover_data=['Status'], labels={'Status':'Race Result'}, hole=.3)
    success.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    success.update_layout(margin=dict(t=100, b=10, l=0, r=0, pad=0))
    success.update_traces(textposition='inside', textinfo='percent+label')
    success.update_layout(showlegend=False)

    dnf.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    dnf.update_layout(margin=dict(t=100, b=10, l=0, r=0, pad=0))
    dnf.update_traces(textposition='inside', textinfo='percent+label')
    dnf.update_layout(showlegend=False)

    return success, dnf

# ----------------------------------------------- CARD CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("total_career_points_card", "children"), 
    Output("total_wins", "children"), 
    Output("highest_position", "children"),
    Output("team_name", "children"),
    Output("driver_number", "children"),
    Input("chosen_driver","value"))
def driver_cards(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    career_points = driver_df["Points"].sum()
    total_wins = driver_df.query("Position == 1").sum()["Counter"]
    highest_position = driver_df["Position"].min()
    team_name = driver_df["TeamName"][driver_df['Year'].idxmax()]
    driver_number = driver_df["DriverNumber"].values[0]
    return career_points, total_wins, highest_position, team_name, driver_number

@app.callback(
    Output("total_season_points_card", "children"), 
    Input("chosen_year","value"), 
    Input("chosen_driver","value"))
def total_season_points_card(chosen_year, chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year]
    value = driver_year_df["Points"].sum()
    return value

# --------------------------------------------- run server ---------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True)
