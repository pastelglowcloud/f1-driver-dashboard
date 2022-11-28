# --------------------------------------------- setup and imports ---------------------------------------------

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
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
year_dropdown = dcc.Dropdown(id = "chosen_year", options = year_options, value= 2022, clearable = False, style={'margin-bottom': '5%'})
driver_image= dbc.CardImg(id = "driver-img", src = "assets/profiles/Carlos Sainz.png")

driver_info = dbc.CardGroup([
    dbc.Col(
        dbc.Card(
            children=[
                dbc.CardHeader('Nationality'), 
                dbc.CardImg(id = "d_flag", src = "assets/flags/es.png", 
                className="card-img-top img-fluid")]), width=4),
    dbc.Col(
        dbc.Card(
            children=[
                dbc.CardHeader('Number'), 
                dbc.CardBody(id = "driver_number", children = [html.H2("55")], 
                className="border-0 bg-transparent")]), 
                width=4),
    dbc.Col(
        dbc.Card(children=[
            dbc.CardHeader('Team'), 
            dbc.CardBody(id = "team_name", children = [html.H3("Ferrari")], 
            className="border-0 bg-transparent")]), 
            width=4),
], id="kpi_group")

twitter_feed = html.Iframe(srcDoc=''' <a class="twitter-timeline" data-theme="dark" href="https://twitter.com/Carlossainz55"> Tweets by Carlos Sainz </a> 
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>''', height=800, width=300, id = "twitter")

kpi = dbc.CardGroup([
    dbc.Card(children=[dbc.CardHeader('WDC Rank'), dbc.CardBody(id="wdc_rank_card", className="border-0 bg-transparent")]),
    dbc.Card(children=[dbc.CardHeader('Points'), dbc.CardBody(id="total_season_points_card")]),
    dbc.Card(children=[dbc.CardHeader('Podiums: 2018-22'),dbc.CardBody(id="total_podiums")]),
    dbc.Card(children=[dbc.CardHeader('Best Position: 2018-22'), dbc.CardBody(id="highest_position")]),
])

success_pie = dcc.Graph(id="card_success")
dnf_pie = dcc.Graph(id="card_dnf")

graph_overall_progress = dcc.Graph(id="overall_progression", className="graph")

graph_total_points = dcc.Graph(id="bar_points_total", className="graph")
graph_circuit_quali = dcc.Graph(id="circuit-quali", className="graph")
graph_circuit_result = dcc.Graph(id="circuit-result", className="graph")

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
            [dbc.Col(id = "section1", width=4, children = [ 
                dbc.Row(driver_image),
                dbc.Row(driver_info),
                dbc.Row(twitter_feed),
                dbc.Row([success_pie, dnf_pie]),
                ]),
            dbc.Col(id = "section2", width=8, children = [
                dbc.Row(kpi),
                dbc.Row(graph_overall_progress), 
                dbc.Row(graph_circuit_quali), 
                dbc.Row(graph_circuit_result), 
                dbc.Row(graph_total_points),
                dbc.Row(graph_position_scatter)
            ]),
        ]),
        dbc.Row([table])
    ])

# ----------------------------------------------- DRIVER INFO CALLBACKS -------------------------------------------------- #

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

@app.callback( 
    Output("team_name", "children"),
    Output("driver_number", "children"),
    Input("chosen_driver","value"))
def driver_cards(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    team_name = driver_df["TeamName"][driver_df['Year'].idxmax()]
    driver_number = driver_df["DriverNumber"].values[0]
    return team_name, driver_number

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
    fig = go.Figure(
        data=[go.Table(
        header=dict(
            values=list(season_summary.columns),
            fill_color='#e45756',align='center'),
        cells=dict(
            values=[season_summary.RoundNumber, season_summary.EventDate, season_summary.GP, season_summary.EventFormat, season_summary.Location, season_summary.QualiStatus, season_summary.GridPosition, season_summary.ResultType, season_summary.Status, season_summary.Position, season_summary.Points, season_summary.CumulativePoints], 
            fill_color = 'rgba(0, 0, 0, 0)', 
            align='center'))])
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(title_text=f'{chosen_year} Season Summary', title_x=0.5)
    fig.update_layout(font_color='#f5f5dc', title_font_color='#f5f5dc')
    fig.update_layout(margin=dict(t=100, b=100, l=0, r=0, pad=0))
    fig.update_layout(height=1500)
    fig.layout.template = 'plotly_dark'
    return fig

# ----------------------------------------------- BAR CALLBACKS -------------------------------------------------- #

@app.callback(
    # Output("bar_points_avg", "figure"), 
    Output("bar_points_total", "figure"),
    Output("circuit-quali", "figure"),
    Output("circuit-result", "figure"),
    Input("chosen_driver","value"))
def fig_avg_bar_pts(chosen_driver):

    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_yr_summary = driver_df.groupby('Year').agg(TotalPoints = pd.NamedAgg(column="Points", aggfunc=sum), TeamName = pd.NamedAgg(column="TeamName", aggfunc=max), 
        TotalRaces = pd.NamedAgg(column="Counter", aggfunc=sum)).reset_index()
    driver_yr_summary["AveragePoints"] = driver_yr_summary.TotalPoints / driver_yr_summary.TotalRaces

    total_points_figure = px.bar(driver_yr_summary, x='Year', y='TotalPoints', color='TeamName', text_auto=True, opacity=0.9, color_discrete_sequence=px.colors.qualitative.T10)

    #circuit quali graph
    quali = driver_df [['Country', 'QualiStatus', 'Counter']]
    quali = quali.groupby(['Country', 'QualiStatus'])['Counter'].sum().reset_index()
    circuit_quali_figure = px.bar(quali, x="Country", y="Counter", color="QualiStatus", text_auto=True, opacity=0.9, color_discrete_sequence=px.colors.qualitative.T10)

    #circuit result graph
    res = driver_df[['Country', 'ResultType', 'Counter']]
    res = res.groupby(['Country', 'ResultType'])['Counter'].sum().reset_index()
    circuit_result_figure = px.bar(res, x="Country", y="Counter", color="ResultType", text_auto=True, opacity=0.9, color_discrete_sequence=px.colors.qualitative.T10)

    #formatting
    total_points_figure.update_xaxes(visible=True, type='category', title=None)
    total_points_figure.update_yaxes(visible=False, showticklabels=False)
    total_points_figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), legend_title="")
    total_points_figure.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    total_points_figure.update_layout(title={'text': 'Points by Season 2018-22','x':0.5})
    total_points_figure.update_layout(margin=dict(t=100, b=10, pad=0))
    total_points_figure.layout.template = 'plotly_dark'
    circuit_quali_figure.update_xaxes(visible=True, type='category', title=None)
    circuit_quali_figure.update_yaxes(visible=False, showticklabels=False)
    circuit_quali_figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), legend_title="")
    circuit_quali_figure.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    circuit_quali_figure.update_layout(title={'text': 'Qualifying Result by Circuit: 2018-22','x':0.5})
    circuit_quali_figure.update_layout(margin=dict(t=100, b=10, pad=0))
    circuit_quali_figure.layout.template = 'plotly_dark'
    circuit_result_figure.update_xaxes(visible=True, type='category', title=None)
    circuit_result_figure.update_yaxes(visible=False, showticklabels=False)
    circuit_result_figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), legend_title="")
    circuit_result_figure.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    circuit_result_figure.update_layout(title={'text': 'Race Result by Circuit: 2018-22','x':0.5})
    circuit_result_figure.update_layout(margin=dict(t=100, b=10, pad=0))
    circuit_result_figure.layout.template = 'plotly_dark'
    return total_points_figure, circuit_quali_figure, circuit_result_figure

# ----------------------------------------------- LINE & AREA CALLBACKS  -------------------------------------------------- #

@app.callback(
    Output("overall_progression", "figure"), 
    Input("chosen_driver","value"),
    Input("chosen_year","value"))
def fig_overall_progression(chosen_driver, chosen_year):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[driver_df['Year'] == chosen_year] # can use query instead for conciseness
    season_summary = driver_year_df[['RoundNumber', 'EventDate', 'GP', 'EventFormat', 'Location', 'QualiStatus', 'GridPosition','ResultType', 'Status', 'Position', 'Points']]
    season_summary['CumulativePoints'] = season_summary['Points'].cumsum()
    season_summary['GP'] = season_summary['GP'].str.replace('Grand Prix','GP')
    fig = go.Figure(
    go.Scatter(x=season_summary["GP"], y=season_summary["CumulativePoints"], mode="lines+markers+text", textposition="top center", name="Cumulative Points"))
    fig.update_layout(title="Error Trend")
    fig.add_trace(go.Bar(x=season_summary["GP"], y=season_summary["Points"], text=season_summary["Points"],name="Points each Race"))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),hovermode="x", legend_title="",)
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(title={'text': f"{chosen_year} Season Overview",'x':0.5})
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(showgrid=False, title=None)
    fig.update_layout(margin=dict(t=100, b=10,r=0, pad=0))
    fig.layout.template = 'plotly_dark'
    return fig

# ----------------------------------------------- SCATTER CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("scatter", "figure"), 
    Input("chosen_driver","value"))
def fig_scatter(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_df["Year"] = driver_df["Year"].astype(str)
    fig = px.scatter(
        data_frame = driver_df, 
        x = "GridPosition", 
        y = "Position", 
        range_x = [0,20], 
        range_y = [0,25], 
        color = "TeamName", 
        trendline="ols", 
        trendline_scope= "overall", 
        color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_layout(
        legend = dict(
            orientation = "h", 
            yanchor = "bottom", 
            y = 1.02, 
            xanchor = "right", 
            x = 1), 
        hovermode = "x", 
        legend_title = "",)
    fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    fig.update_layout(title={'text': 'Correlation between Grid Position and Final Result','x':0.5}, font=dict(color="white"))
    fig.update_xaxes(showgrid = False)
    fig.update_yaxes(showgrid = False)
    fig.update_layout(margin=dict(t=100, b=100, r=0, pad=0))
    fig.layout.template = 'plotly_dark'
    return fig

# ----------------------------------------------- PIE CALLBACKS -------------------------------------------------- #

@app.callback(
    Output("card_success", "figure"), 
    Output("card_dnf", "figure"),
    Input("chosen_year","value"),
    Input("chosen_driver","value"))
def update_pies(chosen_year, chosen_driver):
    # define data
    driver_df = df.loc[df['FullName'] == chosen_driver]
    driver_year_df = driver_df.loc[df['Year'] == chosen_year]
    driver_df_dnf = driver_year_df[["Counter", "Status"]]
    driver_df_dnf = driver_df_dnf.query("Status != 'Finished'").query("Status != '+1 Lap'").query("Status != '+2 Laps'")
    # pie 1
    success = px.pie(driver_year_df, values='Counter', names='ResultType', color_discrete_sequence=px.colors.qualitative.T10, hole=.5)
    success.update_layout(title={'text': f"Race Results: {chosen_year} Season",'x':0.5})
    success.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    success.update_layout(margin=dict(t=100, b=10, l=0, r=0, pad=0))
    success.update_traces(textposition='inside', textinfo='percent+label')
    success.update_layout(showlegend=False)
    success.layout.template = 'plotly_dark'
    # pie 2
    dnf = px.pie(
        data_frame = driver_df_dnf, values ='Counter', names = 'Status',color_discrete_sequence=px.colors.qualitative.T10, 
        hover_data=['Status'], labels={'Status':'Race Result'}, hole=.5)
    dnf.update_layout(title={'text': f"Causes of DNF: {chosen_year} Season",'x':0.5})
    dnf.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"})
    dnf.update_layout(margin=dict(t=100, b=10, l=0, r=0, pad=0))
    dnf.update_traces(textposition='inside', textinfo='percent+label')
    dnf.update_layout(showlegend=False)
    dnf.layout.template = 'plotly_dark'

    return success, dnf

# ----------------------------------------------- CARD CALLBACKS -------------------------------------------------- #

@app.callback( 
    Output("total_podiums", "children"), 
    Output("highest_position", "children"),
    Input("chosen_driver","value"))
def driver_cards(chosen_driver):
    driver_df = df.loc[df['FullName'] == chosen_driver]
    category_races = driver_df[["ResultType", "Counter"]].groupby('ResultType').sum().reset_index()
    total_podiums = category_races.loc[category_races['ResultType'] == "Podium"]["Counter"].values[0]
    highest_position = driver_df["Position"].min()
    return total_podiums, highest_position

@app.callback(
    Output("total_season_points_card", "children"), 
    Output("wdc_rank_card", "children"),
    Input("chosen_year","value"), 
    Input("chosen_driver","value"))
def total_season_points_card(chosen_year, chosen_driver):
    year_df = df.loc[df['Year'] == chosen_year]
    season_summary = year_df[['FullName','Points']]
    agg_df = season_summary.groupby(['FullName']).sum()
    agg_df["Rank"] = agg_df.rank(ascending=False)
    agg_df = agg_df.reset_index()
    driver_year_df = year_df.loc[year_df['FullName'] == chosen_driver]
    season_points = driver_year_df["Points"].sum()
    wdc_rank = agg_df.loc[agg_df["FullName"] == chosen_driver]["Rank"]
    return season_points, wdc_rank

# --------------------------------------------- run server ---------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True)