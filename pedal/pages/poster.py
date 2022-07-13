from subprocess import call
import dash
from dash import html, dcc, dash_table, Input, Output,State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pyparsing import line
import utils_fx, utils_loading
import datetime


dash.register_page(__name__, path_template="/poster/<activity_name>")
px.set_mapbox_access_token('pk.eyJ1IjoibWFnbnVzLXppZWdsZXItY2FwIiwiYSI6ImNsNWNjaDVzcTBnN2gzbG9lZzdhamNwczYifQ.3B2q_3092uMTZHp4ljh8RA')
mapbox_token_public = 'pk.eyJ1IjoibWFnbnVzLXppZWdsZXItY2FwIiwiYSI6ImNsNWNjaDVzcTBnN2gzbG9lZzdhamNwczYifQ.3B2q_3092uMTZHp4ljh8RA'
mapbox_token_mz = 'pk.eyJ1IjoibWFnbnVzLXppZWdsZXItY2FwIiwiYSI6ImNsNWNkOHZscDBnaWQzY3Nla3VjdzU2MjYifQ.Hy-tx1CaYY2Ctwq5QiwWhg'

## statics
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\pedal\\activities\\"
default_loading_format = '.json'

@callback(
    Output('posterpage-df', 'data'),
    Input('activity-page-header', 'children')
    )
def load_activity(activity_name):
    print(activity_name)
    activity = utils_loading.load(default_input_path + activity_name[7:] + default_loading_format)
    return activity.to_json(date_format='iso', orient='split') #need to dump to memory in json

@callback(
    Output('posterpage-poster','figure'),
    Input('posterpage-df', 'data'),
    )
def create_poster(activity):
    activity = pd.read_json(activity, orient='split')

    fig = px.line_mapbox(data_frame=activity,
        lat=activity["lat"].iloc[0:-1:5],
        lon=activity["lon"].iloc[0:-1:5],
        center={'lat':activity['lat'].mean(), 'lon':activity['lon'].mean()},
        height=1080,
        width=1920)
    fig.update_layout(
        mapbox_style='light',
        mapbox_accesstoken=mapbox_token_public)
    fig.update_mapboxes(
        pitch=40,
        # zoom=12
    )

    return fig

def layout(activity_name=None):

    layout = html.Div(children=[
        html.H2(children=f"Poster:{activity_name}",
                id='activity-page-header'),
        dcc.Graph(
            id='posterpage-poster'),
        # dcc.Store stores the activity dataframe
        dcc.Store(id='posterpage-df', storage_type='memory'),
        ])

    return layout