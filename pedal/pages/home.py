import dash
from dash import html, dcc

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='Homepage'),

    html.Div(children='''
        This is the homepage
    '''),

    html.Img(
        src="./assets/bike.jpg",
        width=910,
        height=540)

])