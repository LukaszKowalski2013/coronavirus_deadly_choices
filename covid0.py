import os

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots

############style############:
# DARK SIDE
# dbc_style = dbc.themes.DARKLY
# colors = {
#     'background': '#111111',
#     'text': '#FFFFFF'
# }
# dropdown_button_color = '#d10000'
mapbox_style = "carto-darkmatter"  # DOES NOT MATTER NOW
# what_if_colors= ("#656565", "#4b4b4b", "#a31212")
# what_if_line_color = 'black'
# almost_black = '#191919'
# tickfont_color = '#FFFFFF'
# sparkline_annotation_text_color = "#c1d542"
# sparkline_arrow_color = "#c1d542"
# what_if_deaths_plot = "plotly_dark"
sparkline_color = '#59c41a'
# bright side
my_dbc_style = dbc.themes.MATERIA
colors = {
    'background': '#FFFFFF',  # white
    'text': '#111111',
    'official_covid': '#c12900',
    'excess_deaths': '#6b1ea4'
}
dropdown_button_color = '#e8393f'
what_if_colors = ('#b1b1b1', '#8b8b8b', '#e8393f')  # grey, dark grey, red
what_if_line_color = '#111111'  # white
what_if_average_color = '#000000'  # black
almost_black = '#ededed'  # inverted
tickfont_color = '#111111'
sparkline_annotation_text_color = "#1ea226"
sparkline_arrow_color = "#1ea226"
plotly_template = "plotly_white"

############data############:
app = Dash(__name__, external_stylesheets=[my_dbc_style])
server = app.server

# Get the current directory (root of your GitHub repository)
current_directory = os.path.dirname(__file__)

# csv_file_path = os.path.join(current_directory, relative_path_to_csv)
df_path = os.path.join(current_directory, 'data/output_data/eu_countries/df_yearly.csv')
df = pd.read_csv(df_path)

covid2 = pd.read_csv(os.path.join(current_directory, 'data/output_data/covid2.csv'))

ranking_list = list(zip(covid2.ranking, covid2.country))
xy_ranking = pd.read_csv(os.path.join(current_directory, 'data/gdf_ranking.csv'))
covid_deaths = pd.read_csv(os.path.join(current_directory, "data/output_data/_selected_eu/df_weekly_merged.csv"))
my_eurostat_healthcare_ranking = pd.read_csv(
    os.path.join(current_directory, 'data/my_eurostats_healthcare_ranking.csv'))

df_weekly = pd.read_csv(
    os.path.join(current_directory, "data/output_data/_selected_eu/df_weekly_mine_and_other_sources.csv"))

header_image_link = 'https://drive.google.com/uc?export=view&id=1IZDgtGb8Tn-DRR20YfYr-xQSAmk78FyR'

icons_money = 'https://drive.google.com/uc?export=view&id=16gR6pwHxyMuFCqhjcfJvE-7V6dgl5MEB'
icons_dr = 'https://drive.google.com/uc?export=view&id=1sRDt-fZVi2PZJ-He7PfpIkie9WFF33BH'
icons_nurse = 'https://drive.google.com/uc?export=view&id=1UmlBsyt8P9uhX3aBQIC3i5uagJ-ybaqQ'
icons_beds = 'https://drive.google.com/uc?export=view&id=14mF_YW6-DHKVdGgQBrQ1IUjbmcTIk_WH'
icons_temp = 'https://drive.google.com/uc?export=view&id=1IxQa7Lwn6dPKiszMTPhpyMi3dIKPSXDW'

############ methods ############:
polices = pd.read_csv(os.path.join(current_directory, "data/output_data/polices.csv"))


def get_what_if_deaths(covid_df, country, country_to_compare='Sweden'):
    expected_deaths = covid_df.loc[covid_df['country'] == country, 'expected deaths (2020-2022)'].values[0]
    excess_deaths = covid_df.loc[covid_df['country'] == country, 'excess deaths (2020-2022)'].values[0]
    excess_deaths_what_if_prc = \
        covid_df.loc[covid_df['country'] == country_to_compare, 'excess deaths in % (2020-2022)'].values[0]
    what_if_deaths = (expected_deaths * excess_deaths_what_if_prc / 100) / 1000
    what_if_deaths = what_if_deaths.round(0).astype(int)
    excess_deaths_in_K = (excess_deaths / 1000).round(0).astype(int)
    return f"{what_if_deaths}K", f"{excess_deaths_in_K}K"


def get_official_covid_deaths_by_country(covid_deaths_df):
    covid_deaths = covid_deaths_df[['location', 'date', 'weekly_cases', 'weekly_deaths']].copy()
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
    covid_deaths.drop("date", axis=1, inplace=True)
    return covid_deaths


# template='plotly'; line_color='black'; colors=("#656565", "#4b4b4b", "#a31212"); country='Poland'
def create_what_if_deaths_explanation(dfy, country='Poland'):
    dfy = dfy.loc[dfy.country == country].copy()
    # only data > 2016 <= 2019
    dfy = dfy.loc[(dfy.year <= 2022) & (dfy.year >= 2016)]
    dfy['description'] = 'deaths before covid years'  # different messages
    dfy_av = dfy.loc[(dfy.year <= 2019) & (dfy.year >= 2016)]
    dfy_av = dfy_av[['country', 'year', 'deaths', 'description']]
    dfy_below = dfy.loc[(dfy.year >= 2020)].copy()
    dfy_above = dfy.loc[(dfy.year >= 2020)].copy()
    dfy_below['description'] = 'deaths below 2016-2019 average'
    dfy_below['deaths'] = dfy_below['avg_deaths']

    dfy_above['description'] = 'excess deaths (above 2016-2019 average)'
    dfy_above['deaths'] = dfy_above['excess_deaths']

    df = pd.concat([dfy_av, dfy_below, dfy_above])
    official_deaths = get_official_covid_deaths_by_country(covid_deaths)
    df = df.merge(official_deaths, on=['country', 'year'], how='left')
    df['deaths_diff'] = df['deaths'] - df['official Covid deaths']

    df = df.loc[df.country == country]
    total_excess_deaths = df.loc[df['description'] == 'excess deaths (above 2016-2019 average)'].sum()['deaths']
    total_official_covid_deaths = df.loc[df['description'] == 'excess deaths (above 2016-2019 average)'].sum()[
        'official Covid deaths']
    links = '<a href="https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Excess_mortality_-_statistics#Excess_mortality_in_the_EU_between_January_2020_and_May_2023/">Eurostat</a>, ' \
            '<a href="https://github.com/owid/covid-19-data/">JHU CSSE/Our World in Data</a>'

    datasource_note = f"data sources/read more: {links}"
    if total_excess_deaths > total_official_covid_deaths:
        lower_higher = f"The excess deaths were {total_excess_deaths / total_official_covid_deaths:.2f} times higher_lower than expected."
    else:
        lower_higher = f""

    message = f"{country} experienced {(total_excess_deaths / 1000).round(0).astype(int)}k  excess deaths during the 'Covid years' (2020-2022) " \
              f"compared to previous years, with only {(total_official_covid_deaths / 1000).round(0).astype(int)}k officially attributed to coronavirus." \
              + lower_higher

    return df, message, datasource_note


def create_what_if_deaths_plot(df, country='Poland', template=plotly_template, line_color=what_if_average_color,
                               colors=what_if_colors):
    fig = px.bar(df, x='year', y='deaths',
                 hover_data=['description', 'deaths'], color='description',
                 color_discrete_sequence=colors,  # labels={'pop':'population of Canada'},
                 template=template, height=523)

    fig.add_hline(y=df['avg_deaths'].mean(), line_width=3, line_dash="dash", line_color=what_if_average_color,
                  annotation_text="average 2016-2019 deaths", annotation_position="top left",  # "bottom left"
                  annotation_font=dict(size=17))

    fig.update_layout(title_text=f"excess deaths in {country}", title_font_size=17, title_x=0.5, title_y=0.9,
                      legend=dict(orientation="h"))  # , y=-0.3)) #, margin=dict(l=50, r=50, b=150, t=150, pad=4),)

    # fig.write_html("test.html", auto_open=True)
    return fig


def create_covid_excess_deaths(covid2):
    title = "<b>Deadly Choices - Coronavirus Ranking</b>" \
            "<br>232,000 more Polish people died from 2020 to 2022 than we would have expected based on the average from 2016 to 2019." \
            "<br>Our nation has been dealing with the pandemic as one of the worst in Europe." \
            "<br><br><b>How many Poles would have died if we were another country?</b>"

    fig = px.bar(covid2, x='excess deaths in % (2020-2022)',
                 y="ranking",
                 color='excess deaths in % (2020-2022)',
                 color_continuous_scale='Viridis_r',  # 'Inferno_r', color_discrete_sequence=colors, #["#a31212"],
                 hover_data={'country': False,
                             'deaths (2020-2022)': ':,',  # ':.1f', 'deaths (2016-2019)': '.1f',
                             'average deaths (2016-2019)': ':,',  # '.1f',
                             'expected deaths (2020-2022)': ':,',  # '.1f',
                             'excess deaths (2020-2022)': ':,',  # '.1f',
                             'excess deaths in % (2020-2022)': True,  # '.1f',
                             # 'what if deaths': ':,', # '.1f',
                             'ranking': False,  #
                             },
                 hover_name='ranking',
                 orientation='h',
                 # disable zooming
                 range_x=[0, 25],
                 )
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

    fig.update_layout(showlegend=False, )
    return fig, title


def df_visualization_weekly_short(df_weekly, country='Poland'):
    df = df_weekly[df_weekly['location'] == country]
    columns_to_plot = ['weekly deaths', 'excess deaths']
    vaccination_columns = ['vacination rate']
    google_columns = [
        'workplaces']  # ['retail and recreation', 'grocery and pharmacy', 'residential', 'transit stations', 'workplaces']

    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.042,
                        subplot_titles=("weekly deaths", "weekly cases",
                                        "vaccination rate (% of total population)",
                                        "Government Response Index Average",
                                        "Google mobility in workplaces"
                                        ))
    # hide title 'Subplots'
    fig.update_layout(title_text='')
    for i, column in enumerate(columns_to_plot):
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column, showlegend=False), row=1, col=1, )
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column, showlegend=False), row=1, col=1, )

    # add annotation with arrows that indicate "excess deaths" and "weekly deaths"
    fig.add_annotation(x=df['date'].iloc[50], y=df['weekly deaths'].iloc[50],
                       # arrowcolor="#a6a6a6", #todo check if it is OK in dark mode
                       text="official coronavirus deaths", showarrow=True, arrowhead=1,
                       font=dict(color=colors['official_covid']),
                       )
    fig.add_annotation(x=df['date'].iloc[100], y=df['excess deaths'].iloc[100],
                       # arrowcolor="#a6a6a6", #todo check if it is OK in dark mode
                       text="excess deaths", showarrow=True, arrowhead=1,
                       font=dict(color=colors['excess_deaths']))

    fig.add_trace(go.Scatter(x=df['date'], y=df['weekly cases'], name='weekly cases', showlegend=False), row=2, col=1)
    for i, column in enumerate(vaccination_columns):
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column, showlegend=False), row=3, col=1)
        fig.update_yaxes(range=[0, 100], row=3, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['Government Response Index Average'],
                             name='Government Response Index Average', showlegend=False), row=4, col=1)
    fig.update_yaxes(range=[0, 100], row=4, col=1)
    for i, column in enumerate(google_columns):
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column), row=5, col=1)

    fig.update_yaxes(showline=False, linewidth=1, linecolor=almost_black, mirror=True,
                     tickfont=dict(color=tickfont_color),
                     showgrid=False)
    fig.update_xaxes(showline=False, linewidth=1, linecolor=almost_black, mirror=True,
                     tickfont=dict(color=tickfont_color),
                     showgrid=False)
    fig.update_xaxes(tick0=0, dtick=3 * 30 * 24 * 60 * 60 * 1000, tickformat="%b-%Y", tickangle=90)

    fig.update_layout(height=700,
                      showlegend=False,
                      # legend=dict(orientation="h", yanchor="bottom", y=0, xanchor="right", x=1,
                      #             bgcolor='rgba(0,0,0,0.23)'),
                      plot_bgcolor=colors['background'], paper_bgcolor=almost_black, font_color=colors['text']),
    # legend_bgcolor=almost_black)
    # change padding between subplots
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=700)

    return fig


def create_covid_policy_sparklines_for_country_subset(df, country, color=sparkline_color):
    all_indices = ['School closing', 'Workplace closing', 'Cancel public events', 'Restrictions on gatherings',
                   'Stay at home requirements', 'Restrictions on internal movement']
    covid = df.copy()
    covid = covid.loc[covid['country'] == country].copy()
    # change all values to 0 or 1

    fig = make_subplots(rows=len(all_indices), cols=1, shared_xaxes=True,

                        subplot_titles=all_indices, vertical_spacing=0.1)
    row = 1
    for variable in all_indices:
        fig.append_trace(go.Scatter(
            x=covid['date'],
            y=covid[variable],
            line=dict(width=1, color=color),
            name=variable,
        ), row=row, col=1)
        fig.layout.annotations[row - 1].update(text=f'{variable} ({covid[variable].count()})')
        if variable == 'School closing':
            fig.append_trace(go.Scatter(
                x=covid['date'],
                y=covid['All School closing'],
                name='All',
                # line thickness to 3
                line=dict(width=5, color=color)
            ), row=row, col=1)
            days = covid[variable].count() + covid["All School closing"].count()
            fig.layout.annotations[row - 1].update(text=f'All/selected schools closing ({days} days)')
            # add annotation with arrow that indicate "All School closing"

            if covid['All School closing'].notnull().values.any():
                first_index = covid['All School closing'].first_valid_index()
                first_index = covid['All School closing'].index.get_loc(first_index)
                fig.add_annotation(x=covid['date'].iloc[first_index], y=covid['All School closing'].iloc[first_index],
                                   text="All", showarrow=True, arrowhead=1, arrowwidth=2,
                                   arrowcolor=sparkline_arrow_color,
                                   font=dict(color=sparkline_annotation_text_color),
                                   yanchor="top", xshift=3)
        if variable == 'Workplace closing':
            fig.append_trace(go.Scatter(
                x=covid['date'],
                y=covid['All Workplace closing'],
                name='All',
                # line thickness to 3
                line=dict(width=5, color=color),
            ), row=row, col=1)
            days = covid[variable].count() + covid["All Workplace closing"].count()
            fig.layout.annotations[row - 1].update(text=f'All/selected workplaces closing ({days})')
        row += 1

    # fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(visible=False, showticklabels=True)
    fig.update_xaxes(showline=False, linewidth=1, linecolor=almost_black, mirror=True,
                     tickfont=dict(color=tickfont_color),
                     showgrid=False)
    fig.update_xaxes(tick0=0, dtick=3 * 30 * 24 * 60 * 60 * 1000, tickformat="%b-%Y", tickangle=90, tickmode='linear', )
    # set start date to 1-Jan-2020 and end date to 31-Dec-2022 for x axis for all subplots
    fig.update_xaxes(range=[pd.to_datetime('2020-01-01'), pd.to_datetime('2022-12-31')])

    fig.update_layout(height=300, showlegend=False,  # show_title=False, # title_text=f'policy response in {country}',
                      plot_bgcolor=colors['background'], paper_bgcolor=almost_black, font_color=colors['text'])
    # change padding between subplots
    fig.update_layout(margin=dict(l=42, r=20, t=20, b=20), height=500)

    return fig


def create_healthcare_rankings(country='Poland'):
    df = my_eurostat_healthcare_ranking.loc[my_eurostat_healthcare_ranking['country'] == country].copy()
    intro_text = f'''#####  Following data represents a state of healthcare system in {country} among other countries in this ranking:'''
    ranks_money = df['rank_healthcare expenditure in 2020 in euro (per inhabitant)'].values[0]
    money_data = df['healthcare expenditure in 2020 in euro (per inhabitant)'].values[0]
    money_old_data = df['healthcare expenditure in 2012 in euro (per inhabitant)'].values[0]
    money_text = f"Healthcare expenditure in 2020 in euro (per inhabitant): {country} has {ranks_money}/28 place in ranking. In 2020 it spent {money_data} euro per inhabitant ({money_old_data} in 2012)."

    dr16 = df['Practising physicians in 2016 (per 100 000 inhabitants)'].values[0]
    dr20 = df['Practising physicians in 2021 (per 100 000 inhabitants)'].values[0]
    rank_dr20 = df['rank_Practising physicians in 2021 (per 100 000 inhabitants)'].values[0]
    dr_text = f"Practising physicians in 2021 (per 100K inhabitants): {country} has {rank_dr20}/28 place in ranking. In 2021 it had {dr20} physicians per 100K inhabitant ({dr16} in 2016)."

    nurses15 = df['Practising nurses in 2015 (per 100 000 inhabitants)'].values[0]
    nurses20 = df['Practising nurses in 2020 (per 100 000 inhabitants)'].values[0]
    rank_nurses20 = df['rank_Practising nurses in 2020 (per 100 000 inhabitants)'].values[0]
    if country == 'Poland':
        nurses_text = f"Practising nurses in 2017 (per 100K inhabitants): {country} has {rank_nurses20}/28 place in ranking. In 2017 it had {nurses20} nurses per 100K inhabitant ({nurses15} in 2015). Note: Eurostat has data for Poland only for 2017, while for other countries for 2020."
    else:
        nurses_text = f"Practising nurses in 2020 (per 100K inhabitants): {country} has {rank_nurses20}/28 place in ranking. In 2020 it had {nurses20} nurses per 100K inhabitant ({nurses15} in 2015)."

    beds09 = df['Curative care beds in hospitals in 2009 (per 100 000 inhabitants)'].values[0]
    beds19 = df['Curative care beds in hospitals in 2019 (per 100 000 inhabitants)'].values[0]
    rank_beds19 = df['rank_Curative care beds in hospitals in 2019 (per 100 000 inhabitants)'].values[0]
    beds_text = f"Curative care beds in hospitals in 2019 (per 100K inhabitants): {country} has {rank_beds19}/28 place in ranking. In 2019 it had {beds19} beds per 100K inhabitant ({beds09} in 2009)."

    if country == 'Poland':
        temporary_beds = '''###### Moreover, according to Supreme Audit Office: "Temporary hospitals in Poland were built in Poland since October 2020 on a scale unseen in Europe, without any plan or reliable analysis of the epidemiological situation or availability of medical staff, and also without any cost calculation – NIK established. According to the Polish SAI over PLN 612.6 million was spent ineffectively and without purpose on the creation, functioning and liquidation of temporary hospitals located in large-format buildings." [NIK](https://www.nik.gov.pl/en/news/ineffective-management-of-the-covid-19-pandemic-in-poland-press-conference-at-nik.html)'''
    else:
        temporary_beds = ''

    healthcare_rankings = html.Div([
        html.Div([dcc.Markdown(children=['''---''', intro_text]),
                  ]),

        html.Div([
            html.Div([
                html.Img(src=icons_money,
                         style={'max-width': '113px', 'height': 'auto', 'display': 'inline-block',
                                'padding': '5px 5px 5px 5px'}),
                dcc.Markdown(children=money_text, style={'display': 'inline-block'}),
            ]),
        ]),

        html.Div([
            html.Div([
                html.Img(src=icons_dr,
                         style={'max-width': '113px', 'height': 'auto', 'display': 'inline-block',
                                'padding': '5px 5px 5px 5px', }),
                dcc.Markdown(children=dr_text, style={'display': 'inline-block'}),
            ]),
        ]),

        html.Div([
            html.Div([
                html.Img(src=icons_nurse,
                         style={'max-width': '113px', 'height': 'auto', 'display': 'inline-block',
                                'padding': '5px 5px 5px 5px', }),
                dcc.Markdown(children=nurses_text, style={'display': 'inline-block'}),
            ]),
        ]),

        html.Div([
            html.Div([
                html.Img(src=icons_beds,
                         style={'max-width': '113px', 'height': 'auto', 'display': 'inline-block',
                                'padding': '5px 5px 5px 5px', }),
                dcc.Markdown(children=beds_text, style={'display': 'inline-block'}),
            ]),
        ]),

        html.Div([
            dcc.Markdown(children=temporary_beds, style={'display': 'inline-block'}),
        ]),

        html.Div([
            # Header image with markdown text
            dcc.Markdown(
                children=['''Note: Healthcare images [designed by macrovector / Freepik](http://www.freepik.com)''']),
        ]),

    ], id='healthcare_rankings')
    return healthcare_rankings


############ layout elements ############
default_country = 'Poland'
dropdown_country = dcc.Dropdown(
    id="dropdown",  # options=df.country.unique()
    # show drop down values based on ranking_list
    options=[{'label': i[0], 'value': i[1]} for i in ranking_list],
    value=default_country,
    # color="danger",
    style={
        # 'width': '73%',
        'background-color': dropdown_button_color,  # colors['background'], #'#656565',
        'color': colors['text'],  # '#a31212',
        'border': '1px solid white',
        'text-align': 'center',
        'margin': 'auto',
        'display': 'block',
        'font-size': '21px',
        # 'font-family': 'Arial',
        # 'font-weight': 'bold',
    }
)

covid_ranking_fig, covid_ranking_title = create_covid_excess_deaths(covid2)
covid_ranking = dcc.Graph(id='covid_ranking', figure=covid_ranking_fig,
                          style={'width': '99%', 'height': '99%', 'display': 'inline-block'},
                          config={'staticPlot': True})

# header_map_fig = render_image_map()
# header_map = dcc.Graph(id='header_map', figure=header_map_fig, style={'width': '99%', 'height': '99%', 'display': 'inline-block'})
# app.layout = html.Div([
#     html.Img(src='data:image/png;base64,{}'.format(encoded_image))
# ])


# website layout
# markdown text with thick red seperator line
header_markdown_text = '''# Deadly Choices - Coronavirus Ranking
'''

intro_markdown_text = '''
During pandemic it became clear, that our decisions impact lives of other human being and that we are all connected. 
The analysis and ranking are based on excess death statistics, since it is the most comparable one across countries 
and it is more reliable than the number of deaths officially attributed to coronavirus (Eurostat 2023; link below).
Excess deaths here are deaths from all causes in the COVID-19 period above deaths before the coronavirus pandemic (2016-2019). The higher the value, the more additional deaths. If the value is negative, it means that there were fewer deaths than in the 'normal period'. This measure is far more comparative than deaths officially attributed to coronavirus for many reasons: hospitals reported coronavirus deaths differently (there might be some incentives to classify someone as a "covid patient), the virus could be one of many reasons why someone died or deaths may be related to country's restrictions (e.g. patient may skip some diagnosis, hospitals were not accepting as many patients as usual).

The long-term effects of the pandemic on excess are yet unknown, but the ranking that I created should be a guideline on how we performed, and how the decisions of our countries impacted the lives of our families. I hope it will help us make proper decisions in life during the next pandemic and future elections.

##### Coronavirus ranking: the worst countries to live in during coronavirus pandemic were Bulgaria, Cyprus, Poland, Romania and Slovakia - there were more then 19% of excess deaths during 2020-2022 period. On the other side of the ranking are: Denmark, Finland, Iceland, Norway and Sweden, with excess deaths lower then 7%.
'''

intro_markdown_text2 = '''
---
# Choose a country, to explore how it dealt with coronavirus pandemic: 
'''

excess_deaths_chart_df, message_excess_deaths, datasource_note = create_what_if_deaths_explanation(df,
                                                                                                   default_country)  # todo get rid of this datasource note - we can wrte it with html
excess_deaths_chart_fig = create_what_if_deaths_plot(excess_deaths_chart_df, default_country,
                                                     plotly_template, what_if_line_color, what_if_colors)

excess_deaths_chart_fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                                      font_color=colors['text'])

excess_deaths_explanation = dcc.Graph(id='excess_deaths_explanation_graph', figure=excess_deaths_chart_fig,
                                      config={'staticPlot': True})

message_excess_deaths_text = html.Div([
    dcc.Markdown(children=message_excess_deaths, id="excess_deaths_message"),
])

what_if_deaths, excess_deaths_in_selected_country = get_what_if_deaths(covid2, default_country,
                                                                       country_to_compare='Sweden')

message_excess_deaths = f"If {default_country} had the same excess deaths percent as Sweden (the best in Europe), " \
                        f"it would have lost {what_if_deaths} people, not {excess_deaths_in_selected_country}. "
message_what_if_deaths = html.Div([
    dcc.Markdown(children=message_excess_deaths, id="message_what_if_deaths"),
])

weekly_charts_text = '''
Explore how coronavirus pandemic unfolded on weekly basis in the selected country.
'''
weekly_charts_intro = dcc.Markdown(children=weekly_charts_text, id="weekly_charts_intro")
weekly_charts_fig = df_visualization_weekly_short(df_weekly, country='Poland')
weekly_charts = dcc.Graph(id='weekly_charts', figure=weekly_charts_fig, config={'staticPlot': False})

polices_fig = create_covid_policy_sparklines_for_country_subset(polices, country='Poland')
polices_charts = dcc.Graph(id='polices_charts', figure=polices_fig, config={'staticPlot': False})

healthcare_rankings = create_healthcare_rankings('Poland')

ending_markdown_text = '''
---
Charts and maps were created based on following data sources:
- Excess deaths were estimated based on Eurostat data on weekly deaths [Eurostat-1](https://data.europa.eu/data/datasets/whum2ir8f4kymrrkj1srq?locale=en)
- Confirmed weekly cases and deaths (chart) [JHU CSSE/Our World in Data](https://github.com/CSSEGISandData/COVID-19)
- Vaccination rate [Our World in Data](https://github.com/owid/covid-19-data)
- Government Response Index Average and data on restrictions [Oxford COVID-19 Government Response Tracker, Blavatnik School of Government, University of Oxford.](https://github.com/OxCGRT/covid-policy-dataset)
- Google mobility change by activity time [Google Mobility Reports] (https://www.google.com/covid19/mobility/)
- Health care expenditure [Eurostat-2](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Healthcare_expenditure_statistics#Healthcare_expenditure)
- Healthcare personnel statistics - physicians [Eurostat-3](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Healthcare_personnel_statistics_-_physicians#Healthcare_personnel)
- Healthcare personnel statistics - nursing and caring professionals [Eurostat-4](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Healthcare_personnel_statistics_-_nursing_and_caring_professionals#Healthcare_personnel_.E2.80.93_nurses)
- Healthcare resource statistics - beds [Eurostat-5](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Healthcare_resource_statistics_-_beds#Hospital_beds)
- Temporary COVID-19 Hospitals [NIK](https://www.nik.gov.pl/aktualnosci/14-zbednych-szpitali-tymczasowych.html)

Healthcare Healthcare images [designed by macrovector / Freepik](http://www.freepik.com)

Broaden your knowledge here:
- [Eurostat article on excess deaths in EU between 2020 and 2023](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Excess_mortality_-_statistics#Excess_mortality_in_the_EU_between_January_2020_and_May_2023/)
- Thomas Hale, Noam Angrist, Rafael Goldszmidt, Beatriz Kira, Anna Petherick, Toby Phillips, Samuel Webster, Emily Cameron-Blake, Laura Hallas, Saptarshi Majumdar, and Helen Tatlow. (2021). “A global panel database of pandemic policies (Oxford COVID-19 Government Response Tracker).” Nature Human Behaviour. https://doi.org/10.1038/s41562-021-01079-8
'''

############ layout ############
app.layout = html.Div(style={
    'max-width': '90%',
    'margin': '5% auto',
},

    children=[
        html.Div([
            # Header image with markdown text
            html.Img(src=header_image_link,
                     style={'width': '100%', 'height': 'auto', 'max-width': '100%', 'margin': '0% auto'},
                     title="excess deaths map"
                     ),
        ]),
        html.Div([
            dcc.Markdown(children=header_markdown_text, style={'max-width': '50%', }, id="header_markdown_text"),
        ]),
        # add thick red seperator line in color of danger
        html.Div(style={'background-color': '#e8393f', 'height': '10px', 'width': '100%'}),

        html.Div([
            dcc.Markdown(children=intro_markdown_text),
        ]),

        # excess_deaths_map,
        covid_ranking,

        html.Div([
            dcc.Markdown(children=intro_markdown_text2),
        ]),
        dropdown_country,

        message_excess_deaths_text,
        message_what_if_deaths,
        excess_deaths_explanation,
        weekly_charts_intro,
        weekly_charts,
        polices_charts,
        create_healthcare_rankings(),
        # add a div with dbc button to redirect to another website:
        html.Div([
            # dcc.Markdown(children='''---'''),
            html.Div([dbc.Button("Explore excess deaths interactive map (opens in new tab)", color="danger",
                                 href="https://www.games4earth.com/excess-deaths-map", target="_blank")
                      ]),
        ]),

        html.Div([dcc.Markdown(children='''---'''),
                  dbc.Button("back to top", color="warning",
                             href="#dropdown", external_link=False,
                             style={'padding': '5px 5px 5px 5px'})
                  #     ,
                  # dbc.NavItem(dbc.NavLink("A link", href="#dropdown")),
                  ]),

        html.Div([
            dcc.Markdown(children=ending_markdown_text),
        ]),

    ]
)


########## callbacks ##########
@app.callback(
    Output("excess_deaths_explanation_graph", "figure"),
    Output("excess_deaths_message", "children"),
    Output("message_what_if_deaths", "children"),
    Output("weekly_charts", "figure"),
    Output("polices_charts", "figure"),
    Output("healthcare_rankings", "children"),
    Input("dropdown", "value"),
)
# callback method, updates all charts in the UI
def update_bar_chart(country):
    excess_deaths_chart_df, message_excess_deaths, datasource_note = create_what_if_deaths_explanation(df, country)
    excess_deaths_chart_fig = create_what_if_deaths_plot(excess_deaths_chart_df, country,
                                                         plotly_template, colors['background'], what_if_colors)

    what_if_deaths, excess_deaths_in_selected_country = get_what_if_deaths(covid2, country,
                                                                           country_to_compare='Sweden')
    if (country == 'Sweden'):
        message_what_if_deaths = f"If {country} had the same excess deaths percent as Bulgaria (the worst in Europe), " \
                                 f"it would have lost {what_if_deaths} people, not {excess_deaths_in_selected_country}. "
    else:
        message_what_if_deaths = f"If {country} had the same excess deaths percent as Sweden (the best in Europe), " \
                                 f"it would have lost {what_if_deaths} people, not {excess_deaths_in_selected_country}. "

    weekly_charts_fig = df_visualization_weekly_short(df_weekly, country=country)
    polices_fig = create_covid_policy_sparklines_for_country_subset(polices, country=country)
    healthcare_rankings = create_healthcare_rankings(country=country)

    return excess_deaths_chart_fig, message_excess_deaths, message_what_if_deaths, weekly_charts_fig, polices_fig, healthcare_rankings


if __name__ == "__main__":
    app.run_server(debug=True)
