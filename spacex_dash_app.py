# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())  # Convert to int for slider
min_payload = int(spacex_df['Payload Mass (kg)'].min())  # Convert to int for slider

# Create a Dash application
app = Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',  # Default value
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # Pie chart for total successful launches count
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: str(i) for i in range(min_payload, max_payload + 1, 1000)},
        value=[min_payload, max_payload]
    ),

    # Scatter chart for correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    success_counts = filtered_df['class'].value_counts()
    labels = ['Success', 'Failure']
    values = [success_counts.get(1, 0), success_counts.get(0, 0)]

    fig = px.pie(
        names=labels,
        values=values,
        title=f'Success Count for {selected_site if selected_site != "ALL" else "All Sites"}'
    )
    return fig

# Callback for the scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # Further filter based on selected launch site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # Color by Booster Version Category
        title='Payload Mass vs. Launch Success',
        labels={'Class': 'Success (1) / Failure (0)'},
        hover_data=['Launch Site']  # Optional: Show Launch Site on hover
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8061)  # Run on port 8061

