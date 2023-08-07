# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    html.Div(children=[
        html.Label('Dropdown'),
        dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),

        html.Br(),
        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
                     ['Montréal', 'San Francisco'],
                     multi=True),

    ], style={'padding': 10, 'flex': 1}),

], style={'display': 'flex', 'flex-direction': 'row'})

if __name__ == '__main__':
    app.run(debug=True)
