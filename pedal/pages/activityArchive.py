from subprocess import call
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import utils_loading
import pandas as pd

## statics
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\"
activities_list = pd.DataFrame(data={})

dash.register_page(__name__)

layout = html.Div(children=[
    html.Div(
        children='Input the base directory for the gpx data'),
        dcc.Input(
            id='archive-input-path',
            value=default_input_path,
            type='text',
            style={'width': '50%', "float":"None", 'display': 'inline-block'},
        ),
    html.Div(children=[
        html.Button(
            children=["Scan Folder"],
            id='button-scan-folder',
            n_clicks=0,
           
            ),
        dcc.Dropdown(
            placeholder="Select Format",
            options=["gpx", 'csv', 'json','xml'],
            id='archive-dropdown-format',
            )
        ],
        style={'width': '50%', "float":"None", 'display': 'inline-block'}
        ),
    html.Div(
        children=["Identified activities",
        html.Table(
            id='archive-table-activities',
            style={'width': '80%', "float":"None", 'display': 'inline-block'}),
        ]),
    ],
)


@callback(
    Output('activities-list','data'),
    Output('archive-table-activities','children'),
    State('archive-input-path','value'),
    State('archive-dropdown-format','value'),
    Input("button-scan-folder","n_clicks"),
    prevent_initial_call = True
)
def list_activities(input_path, format, n_clicks):
    if n_clicks > 0:
        #populate list
        activities_list = utils_loading.get_activities(input_path, format)
        activities_list = pd.DataFrame.from_dict(activities_list)
        
        # if fig:
        #     fig = {}

        fig = update_table(activities_list)

    else:
        activities_list = pd.DataFrame(data=[])
        fig = {}

    return activities_list.to_json(date_format='iso', orient='split'), fig

def update_table(activities_list):

    fig = dash_table.DataTable(
            data=activities_list.to_dict('rows'),
            columns=[{"name": i, "id": i} for i in activities_list.columns],
            style_cell=dict(textAlign='left'),
            cell_selectable=True,
            row_selectable='multi',
            sort_action='native',
            filter_action='native')

    return fig
