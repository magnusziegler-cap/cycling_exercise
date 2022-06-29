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

## statics
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
TEMPfile = './temp.json'

app = Dash(__name__,
        title="pedal",
        update_title="spinning",
        external_stylesheets=external_stylesheets,
        use_pages=True)

theme = {'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
    }

## load data
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\"

#populate list
activities = utils_loading.get_activities(default_input_path, 'gpx')
# utils_loading.batch_convert(default_input_path,'json',default_input_path)

app.layout = html.Div(children=[
    html.H1(children='pedal'),

    html.H2(children = 'Basic Analysis Development',),

    html.H3(children="This is a development/training project by mz"),

    html.Div(
    [
        html.Div(
            dcc.Link(
                f"{page['name']} - {page['path']}", href=page["relative_path"]
            )
        )
        for page in dash.page_registry.values()
    ]
    ),
    dash.page_container,

    # dcc.Store stores the activity dataframe
    dcc.Store(id='activity-df'),
    dcc.Store(id='activities-list'),
])

if __name__ == '__main__':
    app.run_server(debug=True)