# https://towardsdatascience.com/highlighting-click-data-on-plotly-choropleth-map-377e721c5893
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
# from jupyter_dash import JupyterDash
import pandas as pd
import os
from plotly.subplots import make_subplots
from urllib.request import urlopen
import json
import plotly.express as px
import plotly.graph_objects as go
# import geopandas as gpd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from base64 import b64encode
import io
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import geopandas as gpd
df = px.data.election()
geojson = px.data.election_geojson()

# Prepare a lookup dictionary for selecting highlight areas in geojson
district_lookup = {feature['properties']['district']: feature
                   for feature in geojson['features']}

def get_highlights(selections, geojson=geojson, district_lookup=district_lookup):
    geojson_highlights = dict()
    for k in geojson.keys():
        if k != 'features':
            geojson_highlights[k] = geojson[k]
        else:
            geojson_highlights[k] = [district_lookup[selection] for selection in selections]
    return geojson_highlights


def get_figure(selections):
    # Base choropleth layer --------------#
    fig = px.choropleth_mapbox(df, geojson=geojson,
                               color="Bergeron",
                               locations="district",
                               featureidkey="properties.district",
                               opacity=0.5)

    # Second layer - Highlights ----------#
    if len(selections) > 0:
        # highlights contain the geojson information for only
        # the selected districts
        highlights = get_highlights(selections)

        fig.add_trace(
            px.choropleth_mapbox(df, geojson=highlights,
                                 color="Bergeron",
                                 locations="district",
                                 featureidkey="properties.district",
                                 opacity=1).data[0]
        )

    # ------------------------------------#
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=9,
                      mapbox_center={"lat": 45.5517, "lon": -73.7073},
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      uirevision='constant')

    return fig

selections = list(district_lookup.keys())[:5]
fig = get_figure(selections)
fig.show()

# Keep track of the clicked region by using the variable "selections"
selections = set()

# -------------------------------#

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='choropleth',
        figure=fig
    )
])


# -------------------------------#

@app.callback(
    Output('choropleth', 'figure'),
    [Input('choropleth', 'clickData')])
def update_figure(clickData):
    if clickData is not None:
        location = clickData['points'][0]['location']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)

    return get_figure(selections)


# -------------------------------#
app.run_server(mode='inline')