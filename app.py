import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pyodbc
import dash_bootstrap_components as dbc
import os

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define a function to create image paths
def get_image_path(brand):
    if brand == 'Chevrolet':
        return '/assets/images/cheveroletlogo.png'
    elif brand == 'Ford':
        return '/assets/images/fordlogo.png'
    elif brand == 'Honda':
        return '/assets/images/hondalogo.png'
    elif brand == 'Hyundai':
        return '/assets/images/hyundailogo.png'
    elif brand == 'Toyota':
        return '/assets/images/toyotalogo.png'
    else:
        return None

# Define the list of cities and their corresponding latitude and longitude
cities_data = {
    "City": ["Los Angeles", "New York", "Chicago", "Miami", "San Francisco", "Dallas", "Atlanta", "Phoenix", "Houston", "Seattle"],
    "Lat": [34.052235, 40.712776, 41.878113, 25.761681, 37.774929, 32.776665, 33.748997, 33.448376, 29.760427, 47.606209],
    "Lon": [-118.243683, -74.005974, -87.629799, -80.191790, -122.419416, -96.796989, -84.387985, -112.074043, -95.369804, -122.332069]
}

# Create a DataFrame from the cities_data dictionary
df = pd.DataFrame(cities_data)

# Create a scatter map using Plotly Express
map_fig = px.scatter_geo(
    df,
    lat="Lat",
    lon="Lon",
    hover_name="City",
    title="Location",
    template='plotly_dark',  # Set dark background
)

# Define the layout of the app
app.layout = html.Div(style={'backgroundColor': 'black', 'display': 'flex', 'height': '100vh'}, children=[
    # Sidebar
    html.Div(
        className='sidebar',
        children=[
            html.H2("Vehicle Manufacturing Dataset", className="display-4", style={'color': '#333', 'font-size': '24px'}),
            # Add image under "CARWORLD" title
            html.Img(id='brand-logo', style={'width': '80%', 'margin-top': '20px', 'margin-bottom': '20px'}),
            html.P("Make a selection from the dropdown menu", style={'color': '#555'}),
            # Buttons for switching views
            dbc.Button("Graphs", id="btn-graphs", color="danger", className="mb-2", style={'margin-right': '10px'}),
            dbc.Button("Tables", id="btn-tables", color="danger", className="mb-2"),
        ],
        style={
            'flex': '0.1',  # Make the sidebar thinner
            'padding': '2rem',
            'background-color': '#101010',
            'height': '100%',
        }
    ),
    
    # Main content
    html.Div(
        className='content',
        children=[
            html.H1("VMD Analysis Dashboard", className="display-4", style={'color': 'white', 'font-size': '32px'}),
            dcc.Dropdown(
                id='brand-dropdown',
                # Options will be populated dynamically based on data from the database
                options=[
                    {'label': 'Chevrolet', 'value': 'Chevrolet'},
                    {'label': 'Ford', 'value': 'Ford'},
                    {'label': 'Honda', 'value': 'Honda'},
                    {'label': 'Hyundai', 'value': 'Hyundai'},
                    {'label': 'Toyota', 'value': 'Toyota'}
                ],
                value='Toyota',
                multi=False,
                className='plotly_dark',  # Set dropdown to 'plotly_dark' theme
                style={'backgroundColor': 'black', 'color': '#808080'},  # Set background and text color
            ),
            dbc.Row([  # Create a row to contain the charts side by side
                dbc.Col(dcc.Graph(id='price-vs-mileage-scatter', style={'backgroundColor': 'black', 'height': '400px'}, config={'displayModeBar': True}), width=6),
                dbc.Col(dcc.Graph(id='color-distribution-bar', style={'backgroundColor': 'black', 'height': '400px'}, config={'displayModeBar': True}), width=6),
                dbc.Col(dcc.Graph(id='model-pie-chart', style={'backgroundColor': 'black', 'height': '400px'}, config={'displayModeBar': True}), width=6),
                dbc.Col(dcc.Graph(id='location-map', figure=map_fig, style={'backgroundColor': 'black', 'height': '400px'}, config={'displayModeBar': True}), width=6),  # Map chart
            ]),
            # Include the "Graphs" and "Tables" views
            html.Div(id='graphs-view', style={'display': 'block'}),  # Initially visible
            html.Div(id='tables-view', style={'display': 'none'}),  # Initially hidden
        ],
        style={
            'flex': '0.8',  # Make the content area wider
            'padding': '2rem',
            'background-color': 'black',  # Set background color to black
            'height': '100%',
            'color': 'white'  # Set text color to white
        }
    ),
])

# Define CSS styles for the chart container and dropdown menu
app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',
})

# Callback to update the brand logo based on the selected brand
@app.callback(
    Output('brand-logo', 'src'),
    Input('brand-dropdown', 'value'),
)
def update_brand_logo(selected_brand):
    # Update the brand logo
    return get_image_path(selected_brand)

# Callback to update the scatter plot, color distribution bar chart, and model pie chart based on the selected brand
@app.callback(
    [Output('price-vs-mileage-scatter', 'figure'),
     Output('color-distribution-bar', 'figure'),
     Output('model-pie-chart', 'figure')],
    [Input('brand-dropdown', 'value')],
)
def update_plots(selected_brand):
    # Establish the connection to the database
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    server = "carserver1.database.windows.net"
    database = "cardb"
    driver = "{ODBC Driver 18 for SQL Server}"
    
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    connection = pyodbc.connect(conn_str)
    
    # Query data for the selected brand from the database
    query = f"SELECT * FROM CARSINFO WHERE Brand = '{selected_brand}'"
    filtered_df = pd.read_sql(query, connection)
    
    connection.close()
    
    # Scatter plot
    scatter_fig = px.scatter(
        filtered_df, x='Mileage', y='Price', color='Color',
        title=f'Price vs Mileage for {selected_brand} Cars',
        template='plotly_dark',  # Set dark background
    )
    
    # Color distribution bar chart
    color_distribution = filtered_df['Color'].value_counts().reset_index()
    color_distribution.columns = ['Color', 'Count']
    color_fig = px.bar(
        color_distribution, x='Color', y='Count',
        title=f'Color Distribution for {selected_brand} Cars',
        color='Color',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template='plotly_dark',  # Set dark background
    )
    
    # Model pie chart
    model_distribution = filtered_df['Model'].value_counts().reset_index()
    model_distribution.columns = ['Model', 'Count']
    model_pie_fig = px.pie(
        model_distribution, names='Model', values='Count',
        title=f'Model Distribution for {selected_brand} Cars',
        template='plotly_dark',  # Set dark background
    )
    
    return scatter_fig, color_fig, model_pie_fig

# Callback to toggle between "Graphs" and "Tables" views
@app.callback(
    [Output('graphs-view', 'style'),
     Output('tables-view', 'style')],
    [Input('btn-graphs', 'n_clicks'),
     Input('btn-tables', 'n_clicks')]
)
def toggle_views(btn_graphs, btn_tables):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'block'}, {'display': 'none'}
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-graphs':
        return {'display': 'block'}, {'display': 'none'}
    elif button_id == 'btn-tables':
        return {'display': 'none'}, {'display': 'block'}
    
    return {'display': 'block'}, {'display': 'none'}

# Run the app
if __name__ == '__main__': 
    app.run_server(debug=True)
