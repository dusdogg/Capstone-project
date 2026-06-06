# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center',
               'color': '#503D36',
               'font-size': 40}
    ),

    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCSFS SLC 40', 'value': 'CCSFS SLC 40'},
            {'label': 'KSC LC 39A', 'value': 'KSC LC 39A'},
            {'label': 'VAFB SLC 4E', 'value': 'VAFB SLC 4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            int(min_payload): str(int(min_payload)),
            int(max_payload): str(int(max_payload))
        }
    ),

    html.Br(),

    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]
        # Calculate success and failure counts for the selected site
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class_label', 'count'] # Rename for clarity

        fig = px.pie(
            class_counts,
            values='count',
            names='class_label',
            title=f'Total Success Launches for site {entered_site}'
        )

    return fig


# Scatter chart callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(entered_site, payload_range):

    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Launch Outcome for All Sites'
        )
    else:
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Launch Outcome for {entered_site}'
        )

    return fig


if __name__ == '__main__':
    app.run(debug=True)