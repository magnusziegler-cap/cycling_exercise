from datetime import date
from posixpath import split
from dash import Dash, html, dcc, Input, Output, dash_table, State
import dash
from matplotlib.font_manager import json_dump
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn import utils
import utils_loading, utils_fx
import dash_bootstrap_components as dbc
import json

app = Dash(__name__,
        title="pedal",
        update_title="spinning",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        use_pages=True)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2(
            children=["pedal"],
            className="display-4"),
        html.Hr(),
        html.P(
            "Pages", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Activity Archive", href="/activityarchive", active="exact"),
                dbc.NavLink("Activity Statistics", href="/activitystats", active="exact"),
                dbc.NavLink("Visualization(deprecated)", href="/visualization", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    id="page-content",
    children=[dash.page_container],
    style=CONTENT_STYLE)

app.layout = html.Div(
    children=[
        dcc.Location(id="url"),
        sidebar,
        content,
        # dcc.Store stores the activity dataframe
        dcc.Store(id='activity-df', storage_type='memory'),
        dcc.Store(id='activities-list', storage_type='session'),
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)