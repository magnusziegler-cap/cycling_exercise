import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/')

homepage_content_string = "This is a development project, helping me refresh some python, pandas, html, GUI, and visualization skills"

layout = html.Div(children=[
    html.H1(children='Homepage'),

    html.P(children=[homepage_content_string]),

    html.Img(
        src="./assets/bike.jpg",
        width=910,
        height=540)

])

