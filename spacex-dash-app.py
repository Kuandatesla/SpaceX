# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    # Launch site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),

    html.Br(),

    # Pie chart
    dcc.Graph(id='success-pie-chart'),

    html.P("Payload range (Kg):"),

    # Payload slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter chart
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df, names='Launch Site', title='Total Successful Launches by Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df['class'].value_counts().rename({1: 'Success', 0: 'Failure'})
        fig = px.pie(names=counts.index, values=counts.values,
                     title=f'Success vs. Failure for {selected_site}')
    return fig

# Callback for scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=f'Payload vs. Launch Outcome for {"All Sites" if selected_site == "ALL" else selected_site}',
                     labels={'class': 'Launch Outcome'})
    return fig

# Run app
if __name__ == '__main__':
    app.run()
