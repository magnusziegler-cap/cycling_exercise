from subprocess import call
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import utils_loading
import pandas as pd

## statics
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\activities\\"
#activities_list = pd.DataFrame(data={})

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
            dbc.ButtonGroup(children=[
                dbc.Button(
                    children=["Scan Folder"],
                    id='button-scan-folder',
                    n_clicks=0,
                    size='md'
                    ),
                dbc.DropdownMenu(
                    label="Batch Convert to:",
                    id='archive-convert-dropdown',
                    children=[
                        dbc.DropdownMenuItem("JSON",
                            id="batch-convert-json",
                            n_clicks=0),
                        dbc.DropdownMenuItem("CSV",
                            id="batch-convert-csv",
                            n_clicks=0),
                        dbc.DropdownMenuItem("XML",
                            id="batch-convert-xml",
                            n_clicks=0),
                    ]),
                ]),
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
        activities_list = append_links(activities_list)

        # fig = update_table(activities_list)
    
    else:
        activities_list = pd.DataFrame(data=[])
        fig = {}

    return activities_list.to_json(date_format='iso', orient='split') #, fig

@callback(
Output('archive-table-activities','children'),
Input('activities-list','data')
)
def update_table(activities_list):
    activities_list = pd.read_json(activities_list, orient='split')
    
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

@callback(
    Output("batch-convert-json", "disabled"),
    Input("batch-convert-json", "n_clicks"),
    State('archive-input-path','value'),
)
def convert_to_json(n,input_path):
    if n>0:
        utils_loading.batch_convert(input_path=input_path,output_format='json',output_path=input_path)
        return True
    else:
        return False

@callback(
    Output("batch-convert-xml", "disabled"),
    Input("batch-convert-xml", "n_clicks"),
    State('archive-input-path','value'),
)
def convert_to_xml(n,input_path):
    if n>0:
        utils_loading.batch_convert(input_path=input_path,output_format='xml',output_path=input_path)
        return True
    else:
        return False

@callback(
    Output("batch-convert-csv", "disabled"),
    Input("batch-convert-csv", "n_clicks"),
    State('archive-input-path','value'),
)
def convert_to_csv(n,input_path):
    if n>0:
        utils_loading.batch_convert(input_path=input_path,output_format='csv',output_path=input_path)
        return True
    else:
        return False