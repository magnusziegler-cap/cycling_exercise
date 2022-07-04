import dash
from dash import html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import utils_loading
import pandas as pd
import numpy as np
import plotly.express as px
import utils_loading
import meteostat
from meteostat import Hourly
import datetime

dash.register_page(__name__, path_template="/activity/<activity_name>")

## statics
default_input_path = "C:\\Users\\maziegle\\OneDrive - Capgemini\\Documents\\training\\cycling_exercise\\activities\\"
weather_LUT=pd.DataFrame(columns=['Weather Condition'],
     data=['Clear','Fair','Cloudy','Overcast',
    'Fog','Freezing Fog',
    'Light Rain','Rain','Heavy Rain','Freezing Rain','Heavy Freezing Rain',
    'Sleet','Heavy Sleet','Light Snowfall','Snowfall','Heavy Snowfall',
    'Rain Shower','Heavy Rain Shower','Sleet Shower','Heavy Sleet Shower',
    'Snow Shower','Heavy Snow Shower',
    'Lightning','Hail','Thunderstorm','Heavy Thunderstorm','Storm','Unknown'])
    
@callback(
    Output('activitypage-tabs-content', 'children'),
    Input('activitypage-tabs','value'),
)
def render_tab_content(tab):
    if tab == 'tab1-Polar-Plot':
        return(
        html.Div(children=[
            dbc.Spinner(children=[
                html.Div(
                    children=[
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
                    id='activitypage-graph-polar')
                ])
            ])
        )
    elif tab == 'tab2-Map':
        return(
        html.Div(children=[
            dbc.Spinner([
                dcc.Graph(
                    id='activitypage-graph-map',
                    )
                ])
            ]))
    elif tab == 'tab3-Line':
        return(
        html.Div(children=[
            dbc.Spinner([
                dcc.Graph(
                    id='activitypage-graph-line')
                ])
            ]))
    elif tab == 'tab4-Histogram':
        return(
        html.Div(children=[
            dbc.Spinner([
                dcc.Graph(
                    id='activitypage-graph-hist')
                ])
            ]))
    elif tab == 'tab5-Data':
        return(
        html.Div(children=[
            dbc.Spinner([
                html.Table(id='activitypage-graph-data')
                ])
            ]))

@callback(
    Output('activitypage-df', 'data'),
    Input('activity-page-header', 'children')
    )
def load_activity(activity_name):
    activity = utils_loading.load(default_input_path + activity_name + '.gpx')
    return activity.to_json(date_format='iso', orient='split') #need to dump to memory in json

@callback(
    Output('activitypage-graph-polar', 'figure'),
    Input('activitypage-df', 'data'),
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
    Output('activitypage-graph-map','figure'),
    Input('activitypage-df','data')
)
def update_MapFig(jsondata):
    activity = pd.read_json(jsondata, orient='split')

    fig = px.scatter_mapbox(data_frame=activity,
        lat=activity["lat"],
        lon=activity["lon"],
        color=activity["gradient"],
        range_color=[-5,5],
        center={'lat':activity.iloc[0].lat, 'lon':activity.iloc[0].lon},
        title="Data through the map",
        height=720,
        width=1080,
        mapbox_style="stamen-terrain")

    return fig

@callback(
    Output('activitypage-graph-line', 'figure'),
    Input('activitypage-df', 'data'),
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
    Output('activitypage-graph-data', 'children'),
    Input('activitypage-df', 'data'),
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
    Output('activitypage-graph-hist', 'figure'),
    Input('activitypage-df', 'data'),
    )
def update_HistFig(activity):
    
    activity = pd.read_json(activity, orient='split')

    fig = px.histogram(data_frame=activity,
    x=["cad","hr","power","hr_resting_multiple","gradient"],
    )

    fig.update_layout(transition_duration=100)

    return fig

@callback(
Output("activitypage-weatherinfo", "children"),
Output("activitypage-weathermeaninfo", "children"),
Output("activitypage-weather-table","children"),
Input("activitypage-df",'data')
)
def update_weatherData(activity):
    activity = pd.read_json(activity, orient='split')

    #grab weatherdata from nearest station to starting point if elapsed time is less than 2h (i.e a short ride)
    if(pd.to_timedelta(activity['elapsed_time'].iloc[-1]) <= datetime.timedelta(hours=2)):
        weather_station = meteostat.Point(
                                lat=activity.lat.iloc[0],
                                lon=activity.lon.iloc[0],
                                alt=activity.ele.iloc[0])
    else:
        #else we take the centroid
        weather_station = meteostat.Point(
                                lat=activity.lat.mean(),
                                lon=activity.lon.mean(),
                                alt=activity.ele.iloc[0])

    start_time = pd.to_datetime(activity['time'].iloc[0], yearfirst=True, utc=True).to_pydatetime().replace(tzinfo=None)
    end_time = pd.to_datetime(activity['time'].iloc[-1], yearfirst=True, utc=True).to_pydatetime().replace(tzinfo=None)

    weather_data = Hourly(
                    loc=weather_station,
                    start=start_time,
                    end=end_time)
    weather_data = weather_data.fetch()
    weather_data.dropna(axis='columns', how='all')
    weather_data['coco'] = weather_data['coco'].replace(np.nan, value=27)
    weather_data['coco'] = weather_data['coco'].apply(lambda x:weather_LUT['Weather Condition'].iloc[int(x)])
    weather_data.insert(loc=0, column="time", value=weather_data.index)
    
    print(weather_data)

    ## at start
    weather_string_g = f"The activity started when the weather was classified as: {weather_data.coco.iloc[0]}. "
    weather_string_t = f"The temperature was: {weather_data.temp.iloc[0]} Degrees Celcius, with humidity of: {weather_data.rhum.iloc[0]}%. "
    weather_string_w = f"The wind was: {weather_data.wspd.iloc[0]} km/h, gusting to {weather_data.wpgt.iloc[0]}, blowing: {weather_data.wdir.iloc[0]} degrees. "
    weather_string = weather_string_g + weather_string_t + weather_string_w

    ## mean
    weather_string_gm = f"As a whole, the weather was: {weather_data['coco'].mode()[0]}. "
    weather_string_tm = f"On average the temperature was: {weather_data['temp'].mean().round()} Degrees Celcius, with humidity of: {weather_data.rhum.mean().round()}%. "
    weather_string_wm = f"The wind was typically: {weather_data.wspd.mean().round()} km/h, gusting to {weather_data.wpgt.mean().round()}, and blowing: {weather_data.wdir.mean().round()} degrees. "
    weather_string_mean = weather_string_gm + weather_string_tm + weather_string_wm

    ## table
    weather_table = dash_table.DataTable(data=weather_data.to_dict('records'),
        columns=[{"name": i, "id": i} for i in weather_data.columns],
        style_cell=dict(textAlign='left'),
        cell_selectable=True,
        row_selectable='multi',
        sort_action='native',
        hidden_columns=[],
        filter_action='native')

    return weather_string, weather_string_mean, weather_table

@callback(
Output("activitypage-description", "children"),
Input("activitypage-df",'data'),
Input('activity-page-header', 'children')
)
def update_description(activity, activity_name):
    activity = pd.read_json(activity, orient='split')
    description = f"The activity: {activity_name} was recorded on {activity.time.iloc[0]} and had a duration of: {pd.to_timedelta(activity['elapsed_time'].iloc[-1])}."

    return description

def layout(activity_name=None):

    layout = html.Div(children=[
        html.H2(children=f"{activity_name}",
                id='activity-page-header'),
        dbc.Accordion(
            always_open=True,
            children=[
            dbc.AccordionItem(
                title="Description",
                children=[
                html.Div(children=[
                    dbc.Spinner(children=[
                        html.H3(children="Description:"),
                        html.Article(children=[], id='activitypage-description')
                        ])
                    ])
                ]),
            dbc.AccordionItem(
                title="Weather",
                children=[
                html.Div(children=[
                    dbc.Spinner(children=[
                        html.H3(children="Weather:"),
                        html.P(children=[], id='activitypage-weatherinfo'),
                        html.P(children=[], id="activitypage-weathermeaninfo"),
                        dbc.Table(children=[], id="activitypage-weather-table")
                        ])
                    ])
                ]),
            dbc.AccordionItem(title='Visualization',
                children=[
                    html.Div(children=[
                        html.H3(children=["Visualizations"]),
                        dcc.Tabs(
                            id="activitypage-tabs",
                            value="tabs",
                            children=[
                                dcc.Tab(id="activitypage-polar-plot", label="Polar", value="tab1-Polar-Plot"),
                                dcc.Tab(id="activitypage-map-plot", label="Map", value="tab2-Map"),
                                dcc.Tab(id="activitypage-line-plot", label="Line", value="tab3-Line"),
                                dcc.Tab(id="activitypage-histogram-plot", label="histogram", value="tab4-Histogram"),
                                dcc.Tab(id="activitypage-data-table",label="Data", value="tab5-Data")
                            ]),
                            html.Div(id='activitypage-tabs-content')
                        ],
                        style={'width': '100%', 'float': 'none', 'display': 'inline-block'}),
                ]),
            ]),
        # dcc.Store stores the activity dataframe
        dcc.Store(id='activitypage-df', storage_type='memory')
        ])

    return layout