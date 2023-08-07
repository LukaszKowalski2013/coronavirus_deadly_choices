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

import dash_bootstrap_components as dbc
from base64 import b64encode
import io
from dash import Dash, dcc, html, Input, Output

import geopandas as gpd

############style############:
colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}
# default_width = 1000

############data############:
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
df_path = r'data\output_data\eu_countries\df_yearly.csv'
df = pd.read_csv(df_path)
gdf = gpd.read_file(r"data\eu.geojson")
covid2 = pd.read_csv(r'data\output_data\covid2.csv')
gdf2 = gdf.merge(covid2, left_on='NAME', right_on='country', how='left')
ranking_list = list(zip(covid2.ranking, covid2.country))
xy_ranking = pd.read_csv('data\gdf_ranking.csv')
# df_weekly = pd.read_csv(r"E:\swiat_gis\covid_deadly_choices_data\other_data\_selected_eu\df_weekly_merged.csv")
#
# x = pd.read_csv(r"E:\swiat_gis\covid_deadly_choices_data\other_data\_selected_eu\my_df_weekly.csv")
# x = x[['country', 'date', 'excess_deaths']]
# x['date'] = x['date'].astype('datetime64[ns]')
# #select only data from 2020-2022
# x = x.loc[x.date >= '2020-01-01']
# x = x.loc[x.date < '2023-01-01']
# x['date'] = x['date'].astype('str')
#
# df_weekly = df_weekly.merge(x, left_on= ['location', 'date'],right_on=['country', 'date'], how='outer')
# df_weekly.to_csv("E:\swiat_gis\covid_deadly_choices_data\other_data\_selected_eu\df_weekly_mine_and_other_sources.csv")
df_weekly = pd.read_csv("D:\Inny_Swiat\pythonGames\dash_world\data\output_data\_selected_eu\df_weekly_mine_and_other_sources.csv")
# change all values inside google columns to normal text without underscore
# gdf_ranking = gdf2[['ranking', 'geometry']]
# gdf_ranking['lat'] = gdf_ranking.geometry.centroid.y
# gdf_ranking['lon'] = gdf_ranking.geometry.centroid.x
# gdf_ranking['area'] = gdf_ranking.area
# gdf_ranking.sort_values(by='area', ascending=False, inplace=True)
# gdf_ranking.drop_duplicates(subset=['ranking'], how= 'first', inplace=True)
# gdf_ranking = gdf_ranking[['ranking', 'lat', 'lon']]
############ methods ############:


def get_what_if_deaths(covid_df, country, country_to_compare='Sweden'):
    expected_deaths = covid_df.loc[covid_df['country'] == country, 'expected deaths (2020-2022)'].values[0]
    excess_deaths = covid_df.loc[covid_df['country'] == country, 'excess deaths (2020-2022)'].values[0]
    excess_deaths_what_if_prc = covid_df.loc[covid_df['country'] == country_to_compare, 'excess deaths in % (2020-2022)'].values[0]
    what_if_deaths = (expected_deaths * excess_deaths_what_if_prc / 100)/1000
    what_if_deaths = what_if_deaths.round(0).astype(int)
    excess_deaths_in_K = (excess_deaths/1000).round(0).astype(int)
    return f"{what_if_deaths}K", f"{excess_deaths_in_K}K"

def get_official_covid_deaths_by_country():
    covid_deaths = pd.read_csv(r"D:\Inny_Swiat\pythonGames\dash_world\other_data\_selected_eu\df_weekly_merged.csv")
    covid_deaths = covid_deaths[['location', 'date', 'weekly_cases', 'weekly_deaths']]
    covid_deaths.weekly_deaths.sum()
    # choose deaths from first week of 2023
    covid_deaths.loc[covid_deaths.date == '2023-01-02', 'weekly_deaths'] = covid_deaths['weekly_deaths'] * (
            6 / 7)  # there were six days in this time from previous year
    covid_deaths.weekly_deaths.sum()
    covid_deaths['date'] = covid_deaths['date'].astype('datetime64[ns]')
    # groupby country and year
    covid_deaths = covid_deaths.groupby(['location', pd.Grouper(key='date', freq='Y')]).sum().reset_index()
    covid_deaths['year'] = covid_deaths['date'].dt.year
    covid_deaths.columns = ['country', 'date', 'official Covid cases', 'official Covid deaths', 'year']
    covid_deaths = covid_deaths.loc[covid_deaths['year'] <= 2022]
    covid_deaths.drop("date", axis = 1,inplace=True)
    return covid_deaths

# template='plotly'; line_color='black'; colors=("#656565", "#4b4b4b", "#a31212"); country='Poland'
def create_what_if_deaths_explanation(dfy, country='Poland'):
    dfy = dfy.loc[dfy.country == country].copy()
    #only data > 2016 <= 2019
    dfy = dfy.loc[(dfy.year <= 2022) & (dfy.year >=2016)]
    dfy['description'] = 'deaths before covid years' #different messages
    dfy_av= dfy.loc[(dfy.year <= 2019) & (dfy.year >=2016)]
    dfy_av = dfy_av[['country', 'year', 'deaths', 'description']]
    dfy_below= dfy.loc[(dfy.year >=2020)].copy()
    dfy_above= dfy.loc[(dfy.year >=2020)].copy()
    dfy_below['description'] = 'deaths below 2016-2019 average'
    dfy_below['deaths'] = dfy_below['avg_deaths']

    dfy_above['description'] = 'excess deaths (above 2016-2019 average)'
    dfy_above['deaths'] = dfy_above['excess_deaths']

    df = pd.concat([dfy_av, dfy_below, dfy_above])
    official_deaths = get_official_covid_deaths_by_country()
    df = df.merge(official_deaths, on=['country', 'year'], how='left')
    df['deaths_diff'] = df['deaths'] - df['official Covid deaths']

    df = df.loc[df.country == country]
    total_excess_deaths = df.loc[df['description']=='excess deaths (above 2016-2019 average)'].sum()['deaths']
    total_official_covid_deaths = df.loc[df['description']=='excess deaths (above 2016-2019 average)'].sum()['official Covid deaths']
    links = '<a href="https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Excess_mortality_-_statistics#Excess_mortality_in_the_EU_between_January_2020_and_May_2023/">Eurostat</a>, ' \
            '<a href="https://github.com/owid/covid-19-data/">JHU CSSE/Our World in Data</a>'

    datasource_note = f"data sources/read more: {links}"
    if total_excess_deaths > total_official_covid_deaths:
        lower_higher = f"The excess deaths were {total_excess_deaths/total_official_covid_deaths:.2f} times higher_lower than expected."
    else:
        lower_higher = f""

    message = f"{country} experienced {(total_excess_deaths/1000).round(0).astype(int)}k  excess deaths during the 'Covid years' (2020-2022) " \
              f"compared to previous years, with only {(total_official_covid_deaths/1000).round(0).astype(int)}k officially attributed to coronavirus." \
              +lower_higher

    return df, message, datasource_note

def create_what_if_deaths_plot(df, country='Poland', template='plotly',line_color='black',
                               colors=("#656565", "#4b4b4b", "#a31212")):
    fig = px.bar(df, x='year', y='deaths',
                 hover_data=['description', 'deaths'], color='description',
                 color_discrete_sequence=colors, #labels={'pop':'population of Canada'},
                 template=template, height=523)

    fig.add_hline(y=df['avg_deaths'].mean(), line_width=3, line_dash="dash", line_color=line_color,
                  annotation_text="average 2016-2019 deaths", annotation_position="bottom right",
                  annotation_font=dict(size=17))

    fig.update_layout(title_text=f"excess deaths in {country}", title_font_size=17, title_x=0.5, title_y=0.9,
                      legend=dict(orientation="h")) #, y=-0.3)) #, margin=dict(l=50, r=50, b=150, t=150, pad=4),)

    # fig.write_html("test.html", auto_open=True)
    return fig

#create map with excess deaths per country
def create_map(mapbox_style="carto-darkmatter"):
    fig = px.choropleth_mapbox(gdf2,
                               geojson=gdf2.geometry,
                               locations=gdf2.index,
                               color='excess deaths in % (2020-2022)',
                               color_continuous_scale='Viridis_r', #'Inferno_r',
                               center={"lat": 50, "lon": 10},
                               mapbox_style=mapbox_style,
                               opacity=0.63,
                               zoom=3.7,
                               title="coronavirus ranking (by excess deaths in % - 2020-2022)",

                               hover_name='ranking',
                               hover_data={'country': False,
                                           'deaths (2020-2022)': ':,',  # ':.1f', 'deaths (2016-2019)': '.1f',
                                           'average deaths (2016-2019)': ':,',  # '.1f',
                                           'expected deaths (2020-2022)': ':,',  # '.1f',
                                           'excess deaths (2020-2022)': ':,',  # '.1f',
                                           'excess deaths in % (2020-2022)': True,  # '.1f',
                                           'ranking': False,  #
                                           })
    # # add labels with scattergeo
    # fig.add_trace(go.Scattergeo(
    #     lon=xy_ranking['lon'],
    #     lat=xy_ranking['lat'],
    #     text=xy_ranking['ranking'],
    #     mode='text',
    #     textfont=dict(
    #         family="sans serif",
    #         size=12,
    #         color="white",
    #     ),
    #     showlegend=False,
    # ))
    fig.update_layout(
        plot_bgcolor='rgba(1,1,1,1)', title_x=0.5, title_y=0.97,
        font=dict(color="white"),
        coloraxis_colorbar=dict(
            title="excess deaths <br>in % (2020-2022)",
            thicknessmode="pixels", thickness=20,
        ),
        margin={"r": 20, "t": 20, "l": 20, "b": 20},
    paper_bgcolor='rgba(0,0,0,1)', showlegend=False,
    # set legend location = 'top left',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )

    fig.update_traces(marker_line_color='white', marker_line_width=1)
    return fig

def create_covid_excess_deaths(covid2):
    title = "<b>Deadly Choices - Coronavirus Ranking</b>" \
            "<br>232,000 more Polish people died from 2020 to 2022 than we would have expected based on the average from 2016 to 2019." \
            "<br>Our nation has been dealing with the pandemic as one of the worst in Europe." \
            "<br><br><b>How many Poles would have died if we were another country?</b>"

    fig = px.bar(covid2, x='excess deaths in % (2020-2022)',
                 y="ranking",
                 color='excess deaths in % (2020-2022)',
                 color_continuous_scale='Viridis_r', # 'Inferno_r', color_discrete_sequence=colors, #["#a31212"],
                 hover_data={'country': False,
                             'deaths (2020-2022)': ':,', # ':.1f', 'deaths (2016-2019)': '.1f',
                             'average deaths (2016-2019)': ':,', # '.1f',
                             'expected deaths (2020-2022)': ':,', # '.1f',
                             'excess deaths (2020-2022)': ':,', #'.1f',
                             'excess deaths in % (2020-2022)': True, # '.1f',
                             # 'what if deaths': ':,', # '.1f',
                             'ranking': False, #
                             },
                 hover_name='ranking',
                 orientation='h')
    # set width and height of the figure
    fig.update_layout(
        plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
        font_color=colors['text'],
        height=700,
        title_x=0.5,
        coloraxis_colorbar=dict(
            title="excess deaths in %<br> (2020-2022)",
            thicknessmode="pixels", thickness=20,
        ),
    )

    fig.update_coloraxes(showscale=False)

    fig.update_layout(showlegend=False,)
    return fig, title

def df_visualization_weekly_short(df_weekly, country='Poland'):
    df = df_weekly[df_weekly['location'] == country]
    columns_to_plot = ['weekly deaths', 'excess deaths']
    vaccination_columns = ['vacination rate']
    google_columns = ['retail and recreation', 'grocery and pharmacy', 'residential', 'transit stations', 'workplaces']

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.042,
                        subplot_titles=("weekly deaths", "weekly cases",
                                        "vaccination rate (% of total population)",
                                        "google mobility change (by activity type)"))
    #hide title 'Subplots'
    fig.update_layout(title_text='')
    for i, column in enumerate(columns_to_plot):
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column, showlegend=False), row=1, col=1, )
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column, showlegend=False), row=1, col=1, )

    # add annotation with arrows that indicate "excess deaths" and "weekly deaths"
    fig.add_annotation(x=df['date'].iloc[50], y=df['weekly deaths'].iloc[50], arrowcolor="#a6a6a6",
                          text="official coronavirus deaths", showarrow=True, arrowhead=1, font=dict(color="white"))
    fig.add_annotation(x=df['date'].iloc[100], y=df['excess deaths'].iloc[100], arrowcolor="#a6a6a6",
                            text="excess deaths (week-to-week)", showarrow=True, arrowhead=1, font=dict(color="white"))

    fig.add_trace(go.Scatter(x=df['date'], y=df['weekly cases'], name='weekly cases'), row=2, col=1)
    for i, column in enumerate(vaccination_columns):
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column, showlegend=False), row=3, col=1)
    for i, column in enumerate(google_columns):
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column), row=4, col=1)

    fig.update_yaxes(showline=False, linewidth=1, linecolor='#191919', mirror=True, tickfont=dict(color='#ffffff'),
                     showgrid=False)
    fig.update_xaxes(showline=False, linewidth=1, linecolor='#191919', mirror=True, tickfont=dict(color='#ffffff'),
                     showgrid=False)
    fig.update_xaxes(tick0=0, dtick=30 * 24 * 60 * 60 * 1000, tickformat="%b-%Y", tickangle=90)

    fig.update_layout(height=700, showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=0, xanchor="right", x=1),
                      plot_bgcolor=colors['background'], paper_bgcolor='#191919', font_color=colors['text'])
    # change padding between subplots
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=700)

    return fig


############ layout elements ############
default_country = 'Poland'
dropdown_country = dcc.Dropdown(
    id="dropdown", #options=df.country.unique()
    # show drop down values based on ranking_list
    options=[{'label': i[0], 'value': i[1]} for i in ranking_list],
    value=default_country,
    style={'width': '99%',
           'background-color': '#656565',
           'color': '#a31212',
           'border': '1px solid white',
           'text-align': 'center',
           'margin': 'auto',
           'display': 'block',
           'font-size': '21px',
           'font-family': 'Arial',
           # 'font-weight': 'bold',
           }
)

covid_ranking_fig, covid_ranking_title = create_covid_excess_deaths(covid2)
covid_ranking = dcc.Graph(id='covid_ranking', figure=covid_ranking_fig, style={'width': '99%', 'height': '99%', 'display': 'inline-block'})

excess_deaths_map_fig = create_map()
excess_deaths_map = dcc.Graph(id='excess_deaths_map', figure=excess_deaths_map_fig, style={'width': '99%', 'height': '99%', 'display': 'inline-block'})

# website layout
excess_deaths_chart_df, message_excess_deaths, datasource_note = create_what_if_deaths_explanation(df, default_country) #todo get rid of this datasource note - we can wrte it with html
excess_deaths_chart_fig = create_what_if_deaths_plot(excess_deaths_chart_df, default_country,
                                                     "plotly_dark", 'white', ("#656565", "#4b4b4b", "#a31212"))

excess_deaths_chart_fig.update_layout( plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                                       font_color=colors['text'])

excess_deaths_explanation = dcc.Graph(id='excess_deaths_explanation_graph', figure=excess_deaths_chart_fig)

message_excess_deaths_text = html.Div([
        dcc.Markdown(children=message_excess_deaths, id="excess_deaths_message"),
    ])

what_if_deaths, excess_deaths_in_selected_country = get_what_if_deaths(covid2, default_country, country_to_compare='Sweden')

message_excess_deaths = f"If {default_country} had the same excess deaths percent as Sweden (the best in Europe), " \
                        f"it would have lost {what_if_deaths} people, not {excess_deaths_in_selected_country}. "
message_what_if_deaths = html.Div([
        dcc.Markdown(children=message_excess_deaths, id="message_what_if_deaths"),
    ])

weekly_charts_text = intro_markdown_text2 = '''
Explore how coronavirus pandemic unfolded on weekly basis in the selected country.
'''
weekly_charts_intro = dcc.Markdown(children=weekly_charts_text, id="weekly_charts_intro")
weekly_charts_fig = df_visualization_weekly_short(df_weekly, country='Poland')
weekly_charts = dcc.Graph(id='weekly_charts', figure=weekly_charts_fig)

intro_markdown_text = '''
During pandemic it became clear, that our decisions impact lives of other human being and that we are all connected. 
The analysis and ranking are based on excess death statistics, since it is the most comparable one across countries 
and it is more reliable than the number of deaths officially attributed to coronavirus ([read Eurostat article about excess deaths](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Excess_mortality_-_statistics#Excess_mortality_in_the_EU_between_January_2020_and_May_2023/)).

The worst countries to live in during coronavirus pandemic were Bulgaria, Cyprus, Poland, Romania and Slovakia - there were more then 19% of excess deaths during 2020-2022 period. On the other side of the ranking are: Denmark, Finland, Iceland, Norway and Sweden, with excess deaths lower then 7%.
'''

intro_markdown_text2 = '''
Choose a country, to explore how it dealt with coronavirus pandemic: 
'''


############ layout ############

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Coronavirus - deadly choices',
        style={'textAlign': 'center', 'color': colors['text']}
    ),
    html.Div([
        dcc.Markdown(children=intro_markdown_text),
    ]),

    excess_deaths_map,
    covid_ranking,

    html.Div([
        dcc.Markdown(children=intro_markdown_text2),
    ]),
    dropdown_country,

    message_excess_deaths_text,
    message_what_if_deaths,
    excess_deaths_explanation,
    weekly_charts_intro,
    weekly_charts
])

########## callbacks ##########
@app.callback(
    Output("excess_deaths_explanation_graph", "figure"),
    Output("excess_deaths_message", "children"),
    Output("message_what_if_deaths", "children"),
    Output("weekly_charts", "figure"),
    Input("dropdown", "value"),
)
def update_bar_chart(country):
    excess_deaths_chart_df, message_excess_deaths, datasource_note = create_what_if_deaths_explanation(df, country)
    excess_deaths_chart_fig = create_what_if_deaths_plot(excess_deaths_chart_df, country,
                                                         "plotly_dark", 'white', ("#656565", "#4b4b4b", "#a31212"))

    what_if_deaths, excess_deaths_in_selected_country = get_what_if_deaths(covid2, country,
                                                                           country_to_compare='Sweden')
    if(country == 'Sweden'):
        message_what_if_deaths = f"If {country} had the same excess deaths percent as Bulgaria (the worst in Europe), " \
                            f"it would have lost {what_if_deaths} people, not {excess_deaths_in_selected_country}. "
    else:
        message_what_if_deaths = f"If {country} had the same excess deaths percent as Sweden (the best in Europe), " \
                            f"it would have lost {what_if_deaths} people, not {excess_deaths_in_selected_country}. "

    weekly_charts_fig = df_visualization_weekly_short(df_weekly, country=country)

    return excess_deaths_chart_fig, message_excess_deaths, message_what_if_deaths, weekly_charts_fig

if __name__ == "__main__":
    app.run_server(debug=True)