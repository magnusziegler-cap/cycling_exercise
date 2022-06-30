import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import utils_fx
import utils_loading

dash.register_page(__name__)
## load data
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\activities\\"

#populate list
activities = utils_loading.get_activities(default_input_path, 'gpx')
#utils_loading.batch_convert(default_input_path,'json',default_input_path)

layout = html.Div(children=[
    html.H1(children='This is the visualization page'),

    html.Div(children=[
        html.P(children='Input the base directory for the gpx data'),
        dcc.Input(id='text-input-path',
            value=default_input_path,
            type='text',
            style={'width': '100%'}
        ),
        html.P(children='gpx files identified:'),
        dcc.Dropdown(
            activities['name'],
            id='dropdown-activity',
            value=activities['name'][0],
        ),
    ],
    style={'width': '50%', 'float': 'none', 'display': 'inline-block'}),

    html.Div(children=["Figures",
        dcc.Tabs(
            id="tabs",
            value="tabs",
            children=[
                dcc.Tab(id="tab-polar-plot", label="Polar", value="tab1-Polar-Plot"),
                dcc.Tab(id="tab-map-plot", label="Map", value="tab2-Map"),
                dcc.Tab(id="tab-line-plot", label="Line", value="tab3-Line"),
                dcc.Tab(id="tab-histogram-plot", label="histogram", value="tab4-Histogram"),
                dcc.Tab(id="tab-data-table",label="Data", value="tab5-Data")
            ]),
            html.Div(id='tabs-content')
    ],
    style={'width': '100%', 'float': 'none', 'display': 'inline-block'}),
     # dcc.Store stores the activity dataframe
    # dcc.Store(id='activity-df')

])


@callback(
    Output('tabs-content', 'children'),
    Input('tabs','value'),
    Input('activity-df',"data")
)
def render_tab_content(tab, activity):
    if tab == 'tab1-Polar-Plot':
        return(
        html.Div(children=[
            html.Div(children=[
                "Select Variable for Radius: ",
                dcc.Dropdown(
                    options=["hr_resting_multiple", "power", "cad", "gradient","up_or_down_bin"],
                    multi=False,
                    id='dropdown-key-radius',
                    value="hr_resting_multiple",
                    style={"width":"50%", "display":"inline-block"}
                    )],
                ),
            html.Div(children=[
                "Select Variable for Colour: ",
                dcc.Dropdown(
                    options=["hr_resting_multiple", "power", "cad", "gradient","up_or_down_bin"],
                    multi=False,
                    id='dropdown-key-colour',
                    value="power",
                    style={"width":"50%", "display":"inline-block"}
                )],
                ),
            dcc.Graph(
                id='graph-polar')
            ]))
    elif tab == 'tab2-Map':
        return(
        html.Div(children=[
            dcc.Input(
                id='input-latlongshift',
                value='lat,long,ele in comma separated input',
                type='text'
            ),
            html.Button(
                children='Apply Lat/Long Shift',
                id = "button-latlongshift-map",
                n_clicks=0,
                ),
            html.P(
                id="text-latlongshift",
                children="",
            ),
            dcc.Graph(
                id='graph-map',
                )
            ]))
    elif tab == 'tab3-Line':
        return(
        html.Div(children=[
            dcc.Graph(
                id='graph-line')
            ]))
    elif tab == 'tab4-Histogram':
        return(
        html.Div(children=[
            dcc.Graph(
                id='graph-hist')
            ]))
    elif tab == 'tab5-Data':
        # return(
        #     dbc.Container([
        #         dbc.Label('testing the table'),
        #         dbc.Table(id='graph-data')
        #     ])
        # )
        return(
        html.Div(children=[
            html.Table(id='graph-data')
            ]))

@callback(
    Output('activity-df', 'data'),
    Input('text-input-path', 'value'),
    Input('dropdown-activity', 'value')
    )
def load_activity(input_path, activity_name):
    activity = utils_loading.load(input_path + activity_name + '.gpx')
    return activity.to_json(date_format='iso', orient='split') #need to dump to memory in json

@callback(
    Output('graph-polar', 'figure'),
    Input('activity-df', 'data'),
    Input('dropdown-key-radius', 'value'),
    Input('dropdown-key-colour', 'value')
    )
def update_PolarFig(activity, key_radius, key_colour):
    
    activity = pd.read_json(activity, orient='split')
    
    fig = px.scatter_polar(data_frame=activity,
        r=activity[key_radius],
        theta=(360*activity["elapsed_time_s"]/activity["elapsed_time_s"].max()),
        range_r = [1, activity[key_radius].max()*1.05],
        color=key_colour,
        title="Data through the wheel")

    fig.update_layout(transition_duration=500)

    return fig

@callback(
    Output("text-latlongshift","children"),
    Input('button-latlongshift-map','n_clicks'),
    State('input-latlongshift','value'),
    Input('activity-df','data'),
    prevent_initial_call = True
)
def apply_latlongshift(n_clicks, input_latlong, jsondata):
    activity = pd.read_json(jsondata, orient='split')

    if n_clicks>0:
        
        lat, long, ele = input_latlong.split(',')
        lat = float(lat)
        long = float(long)
        ele = float(ele)

        outstr=(f"{n_clicks}+Lat/Long/Ele Shift Applied. New Starting Coordinates: {lat}, {long}, {ele}")

        activity = utils_fx.set_track_origin(activity,lat,long,ele)
    else:
        outstr=None

    activity.to_json(date_format='iso', orient='split')
    #update_MapFig(activity.to_json(date_format='iso', orient='split'))

    return outstr

@callback(
    Output('graph-map','figure'),
    Input('activity-df','data')
)
def update_MapFig(jsondata):
    activity = pd.read_json(jsondata, orient='split')

    fig = px.scatter_geo(data_frame=activity,
        lat=activity["lat"],
        lon=activity["lon"],
        color=activity["gradient"],
        projection='natural earth',
        scope='europe',
        center={'lat':activity.iloc[0].lat, 'lon':activity.iloc[0].lon},
        title="Data through the map")
    fig.update_geos(
        visible=True,
        resolution=50,
        showcountries=True,
        showlakes=True,
        showrivers=True,
        countrycolor="blue",
    )
    fig.update_layout(width=1080, height=720, overwrite=True)

    return fig

@callback(
    Output('graph-line', 'figure'),
    Input('activity-df', 'data'),
    )
def update_LineFig(activity):
    activity = pd.read_json(activity, orient='split')

    fig = px.line(data_frame=activity,
        x=activity["time"],
        y=[activity["speed"],activity["power"],activity["hr"]],
        hover_name="time",
        hover_data=["gradient","hr_resting_multiple"],
        title="Data through Time"
        )

    fig.update_layout(transition_duration=500)

    return fig

@callback(
    Output('graph-data', 'children'),
    Input('activity-df', 'data'),
    )
def update_dataTable(activity):

    activity = pd.read_json(activity, orient='split')
    fig = dash_table.DataTable(data=activity.to_dict('records'),
        columns=[{"name": i, "id": i} for i in activity.columns],
        style_cell=dict(textAlign='left'),
        cell_selectable=True,
        row_selectable='multi',
        sort_action='native',
        hidden_columns=[],
        filter_action='native')

    return fig

@callback(
    Output('graph-hist', 'figure'),
    Input('activity-df', 'data'),
    )
def update_HistFig(activity):
    
    activity = pd.read_json(activity, orient='split')

    fig = px.histogram(data_frame=activity,
    x=["cad","hr","power","hr_resting_multiple","gradient"],
    )

    fig.update_layout(transition_duration=100)

    return fig