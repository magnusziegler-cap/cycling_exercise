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


dash.register_page(__name__,)

DEFAULT_READ_FORMAT = '.gpx'
activity_summary_content_string = "Summary statistics for all available activities will be calculated and displayed. \n *Warning: This can take time*"

layout = html.Div(children=[
    html.Div(children=[
        html.H1(children='Activity Stats'),
        html.P(children=[activity_summary_content_string]),
    ]),
    html.Div(
        children=[
        html.H1(children=["Summary Figures"]),
        dbc.Spinner(children=[
            dcc.Graph(id='activity-summary-map')
        ])
    ]),
    html.Div(
        children=[
        html.H1(children=["Summary Table"]),
        dbc.Spinner(children=[
            dbc.Table(id='activity-summary-table'),
        ])
    ]),
    #keep summary stats stored per session so that recalculating doesn't happen as often
    dcc.Store(id='activity-summary-data', storage_type='session'),
    dcc.Store(id='activity-summary-tracks', storage_type='session') 

])

def get_gps_track(activity, reduce:int=10):
    
    track = {
            'name':activity['name'].iloc[0:-1:reduce],
            'lat':activity['lat'].iloc[0:-1:reduce],
            'lon':activity['lon'].iloc[0:-1:reduce],
            'ele':activity['ele'].iloc[0:-1:reduce]
            }

    return pd.DataFrame(track)

def calculate_summary_stats(activity):

    summary = {
        'name':activity['name'].iloc[0],
        'spd_mean':activity['speed'].mean().round(2),
        'spd_med':activity['speed'].median().round(2),
        'elapsed_time':str(activity['elapsed_time'].iloc[-1]),
        'total_distance':activity['cumulative_distance'].iloc[-1].round(2)}
                 
    return summary

@callback(
    Output('activity-summary-data', 'data'),
    Output('activity-summary-tracks', 'data'),
    Input('activities-list','data')
)
def build_summary_table(jsondata):
    print('building summary')
    col_names = ['name', 'spd_mean','spd_med','elapsed_time','total_distance']
    col_names_track = ['name', 'lat','lon','ele']
    activity_summary_data = pd.DataFrame(columns=col_names)
    tracks = pd.DataFrame(columns=col_names_track)

    activities_list = pd.read_json(jsondata, orient='split')

    for path,name in zip(activities_list['path'], activities_list['name']):
        activity = utils_loading.load(input_path=path+name+DEFAULT_READ_FORMAT)

        summary = pd.Series(calculate_summary_stats(activity))
        track = get_gps_track(activity, reduce=20)

        activity_summary_data = activity_summary_data.append(summary, ignore_index=True)
        tracks = tracks.append(track, ignore_index=True)

    return activity_summary_data.to_json(), tracks.to_json()

@callback(
    Output("activity-summary-table", "children"),
    Input("activity-summary-data","data"),
    Input('activities-list','data')
)
def update_summary_table(activity_summary_data, activities_list):
    activity_summary_data = pd.read_json(activity_summary_data)
    activities_list = pd.read_json(activities_list, orient='split')

    activity_summary_data = pd.concat([activity_summary_data, activities_list['link']], axis=1)

    fig = dash_table.DataTable(data=activity_summary_data.to_dict('records'),
        columns=[{"name": i, "id": i, 'presentation':'markdown'} for i in activity_summary_data.columns],
        style_cell=dict(textAlign='left'),
        cell_selectable=True,
        row_selectable='multi',
        sort_action='native',
        hidden_columns=[],
        filter_action='native')
    return fig

@callback(
    Output("activity-summary-map", "figure"),
    Input("activity-summary-tracks","data")
)
def update_summary_map(tracks):
    
    tracks = pd.read_json(tracks)
    
    fig = px.line_mapbox(
            data_frame=tracks,
            lat="lat",
            lon="lon",
            color="name",
            mapbox_style="stamen-terrain",
            height=1080,
            width=1080)

    # fig = px.scatter_geo(
    #     projection='natural earth',
    #     scope='europe',
    #     width=1080,
    #     height=720
    # )
    # for i, (name) in enumerate(tracks['name'].unique()):
    #     track = tracks.loc[tracks['name'] == name]
    #     lats = pd.Series(track["lat"])
    #     lon = pd.Series(track["lon"])

    #     fig.add_trace(
    #         go.Scattergeo(
    #             lat=lats,
    #             lon=lon,
    #             mode='lines',
    #             name=name,
    #             line= dict(width=1))
    #         )
    # fig.update_geos(
    #     visible=True,
    #     resolution=50,
    #     showcountries=True,
    #     showlakes=True,
    #     showrivers=True,
    #     countrycolor="black",
    #     lakecolor="white",
    #     rivercolor="white",
    #     fitbounds="locations"
    #     )
    
    return fig

