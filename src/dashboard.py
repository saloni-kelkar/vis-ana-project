import pandas as pd
import pyproj
import dash
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt #if using matplotlib
import plotly.express as px #if using plotly
import plotly.graph_objs as go
import geopandas as gpd
from dash import Dash, dcc, html, Input, Output
from datetime import datetime
from plotly.offline import iplot, init_notebook_mode
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


from jupyterlab_dash import AppViewer
viewer = AppViewer()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
fp = "../data/shape/StHimark.shp"
df = pd.read_csv("../data/YInt_cat.csv")
map_df = gpd.read_file(fp)
map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
map_df.columns=['id', 'location', 'geometry']


##word cloud
cat_df = pd.read_csv("../data/YInt_cat.csv")
cat_df['time'] = pd.to_datetime(cat_df['time'])


def get_resourse_and_location(ctx):
    resource = ctx.triggered[0]['prop_id']
    resource = resource[:resource.index('_')]
    location = ctx.triggered[0]['value']['points'][0]['hovertext']
    return resource.capitalize(), location.title()


# ------------------------------------------------------------------------------
# App layout



app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        html.H1("Resource Distribution", style={'text-align': 'center'}),
                        html.Br()
                    ]),
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.H3("Water", style={'text-align': 'center'}),
                                dcc.Graph(id='water_map', figure={}),
                                html.Br()
                            ]),
                            dbc.Col([
                                html.H3("Energy", style={'text-align': 'center'}),
                                dcc.Graph(id='energy_map', figure={}),
                                html.Br()
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H3("Food", style={'text-align': 'center'}),
                                dcc.Graph(id='food_map', figure={}),
                                html.Br()
                            ]),
                            dbc.Col([
                                html.H3("Medical", style={'text-align': 'center'}),
                                dcc.Graph(id='medical_map', figure={}),
                                html.Br()
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H3("Shelter", style={'text-align': 'center'}),
                                dcc.Graph(id='shelter_map', figure={}),
                                html.Br()
                            ]),
                            dbc.Col([
                                html.H3("Transportation", style={'text-align': 'center'}),
                                dcc.Graph(id='transportation_map', figure={}),
                                html.Br()
                            ])
                        ])
                    ]),
                    width=8,
                    style={"overflow": "scroll", "height": "600px"},
                ),
                dbc.Col(
                    html.Div([
                        dbc.Row([
                            html.H3("Trend", style={'text-align': 'center'}),
                            dcc.Graph(id="trend_line", figure={})
                        ])
                    ]
                    ),
                    width=4,
                    style={"overflow": "scroll", "height": "600px"},
                    className="no-scrollbars",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dbc.Row([
                            html.H2("", style={'text-align': 'center'}),
                            dcc.Graph(id='messages', figure={}),
                        ])
                    ]
                    ),
                    width=8
                )

            ]
        )
    ],
    fluid=True
)
'''
app.layout = html.Div([

    html.H1("Resource Distribution", style={'text-align': 'center'}),

    dcc.Dropdown(id="select_resource",
                 options=[
                     {"label": "Water", "value": "Water"},
                     {"label": "Energy", "value": "Energy"},
                     {"label": "Food", "value": "Food"},
                     {"label": "Medical", "value": "Medical"},
                     {"label": "Shelter", "value": "Shelter"},
                     {"label": "Transportation", "value": "Transportation"}],
                 multi=False,
                 value="Water",
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={}),

    dcc.Graph(id='word_cloud', figure={})

])

'''
# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='water_map', component_property='figure'),
     Output(component_id='energy_map', component_property='figure'),
     Output(component_id='food_map', component_property='figure'),
     Output(component_id='medical_map', component_property='figure'),
     Output(component_id='shelter_map', component_property='figure'),
     Output(component_id='transportation_map', component_property='figure'),
     Output(component_id='trend_line', component_property='figure'),
     Output(component_id='messages', component_property='figure')],
    [Input(component_id='water_map', component_property='clickData'),
     Input(component_id='energy_map', component_property='clickData'),
     Input(component_id='food_map', component_property='clickData'),
     Input(component_id='medical_map', component_property='clickData'),
     Input(component_id='shelter_map', component_property='clickData'),
     Input(component_id='transportation_map', component_property='clickData')]
)
def update_graph(water_map_input,
                 energy_map_input,
                 food_map_input,
                 medical_map_input,
                 shelter_map_input,
                 transportation_map_input ):
    ctx = dash.callback_context

    print(ctx.triggered)

    # Water choropleth
    df_cat = df[df.cat == 'Water'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    water_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    water_fig.update_geos(fitbounds="locations", visible=True)
    water_fig.update_layout(
    )
    water_fig.update(layout=dict(title=dict(x=0.5)))
    water_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': ''})

    # Energy choropleth

    df_cat = df[df.cat == 'Energy'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])
    energy_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    energy_fig.update_geos(fitbounds="locations", visible=True)
    energy_fig.update_layout(
    )
    energy_fig.update(layout=dict(title=dict(x=0.5)))
    energy_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': ""})

    # Food choropleth
    df_cat = df[df.cat == 'Food'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    food_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    food_fig.update_geos(fitbounds="locations", visible=True)
    food_fig.update_layout(
    )
    food_fig.update(layout=dict(title=dict(x=0.5)))
    food_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': ''})

    # Medical choropleth
    df_cat = df[df.cat == 'Medical'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    medical_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    medical_fig.update_geos(fitbounds="locations", visible=True)
    medical_fig.update_layout(
    )
    medical_fig.update(layout=dict(title=dict(x=0.5)))
    medical_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': ''})

    # Shelter choropleth
    df_cat = df[df.cat == 'Shelter'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    shelter_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    shelter_fig.update_geos(fitbounds="locations", visible=True)
    shelter_fig.update_layout(
    )
    shelter_fig.update(layout=dict(title=dict(x=0.5)))
    shelter_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': ''})

    # Transportation choropleth
    df_cat = df[df.cat == 'Transportation'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    transportation_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    transportation_fig.update_geos(fitbounds="locations", visible=True)
    transportation_fig.update_layout(
    )
    transportation_fig.update(layout=dict(title=dict(x=0.5)))
    transportation_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': ''})

    #Trend
    if(ctx.triggered[0]['value'] == None):
        resource = "Water"
        location = "Northwest"
    else:
        resource, location = get_resourse_and_location(ctx)
    df_trend = df[(df.cat == resource) & (df.location == location)].groupby(['time', 'location', 'cat']).size().reset_index()
    df_trend.columns = ['time', 'location','cat', 'count']
    trend_fig = px.line(df_trend, x="time", y="count")
    trend_fig.update_layout(title_text= resource+' @ '+location)

    #Messages
    df_messages = df[(df.cat == resource) & (df.location == location)].groupby(
        ['time', 'location', 'cat', 'account', 'message']).size().reset_index()

    messages_fig = go.Figure(data=[go.Table(header=dict(values=['Account', 'Message','location','time']),
                                   cells=dict(values=[df_messages['account'], df_messages['message'], df_messages['location'], df_messages['time']]))
                          ])
    return  water_fig,energy_fig,food_fig,medical_fig,shelter_fig,transportation_fig,trend_fig,messages_fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
    
#viewer.show(app)
