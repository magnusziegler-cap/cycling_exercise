from subprocess import call
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import utils_loading
import pandas as pd

## statics
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\activities\\"
activities_list = pd.DataFrame(data={})

dash.register_page(__name__)

layout = html.Div(children=[
            html.H1(children='Activity Archive'),
            html.P(children=['Input the base directory for the gpx data']),
            dbc.InputGroup(
                [
                dbc.Input(
                    id='archive-input-path',
                    value=default_input_path,  
                    type='text'),
                dbc.Select(
                    placeholder="Select Format",
                    options=[
                        {'label':"gpx", 'value':'gpx'},
                        {'label':"csv", 'value':"csv"},
                        {'label':"json", 'value':"json"},
                        {'label':"xml", 'value':"xml"},
                        ],
                    id='archive-dropdown-format')
                ],
                size='md'
            ),
            dbc.Button(
                children=["Scan Folder"],
                id='button-scan-folder',
                n_clicks=0,
                size='md'
                ),
            html.Div([
                dbc.Spinner(size='md',
                children=[
                    html.H2(
                        children=["Identified activities"]),
                    dbc.Table(
                        id='archive-table-activities'
                        )
                    ]),
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

        fig = update_table(activities_list)

    else:
        activities_list = pd.DataFrame(data=[])
        fig = {}

    return activities_list.to_json(date_format='iso', orient='split'), fig

def update_table(activities_list):
    activities_list = append_links(activities_list)
    cols = [{"name": i, "id": i, 'presentation':'markdown'} for i in activities_list.columns]
    fig = dash_table.DataTable(
            data=activities_list.to_dict('rows'),
            columns=cols,
            style_cell=dict(textAlign='left'),
            cell_selectable=True,
            row_selectable='multi',
            sort_action='native',
            filter_action='native')

    return fig

def append_links(activities_list):
    links = []
    for (name) in activities_list["name"]:
        links.append(f"[{name}](/activity/{name})")
    
    activities_list.insert(loc=0, column="link", value=links)

    return activities_list
