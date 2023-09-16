# Import necessary libraries
import dash
import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pyodbc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import dcc, html
import os 

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define a function to get image paths for different car brands
def get_image_path(brand):
    """
    Given a car brand, return the path to the corresponding brand logo image.

    Args:
        brand (str): The car brand.

    Returns:
        str: The path to the brand logo image.
    """
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

# Define data for cities and their corresponding latitude and longitude
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
    title="City Locations",
    template='plotly_dark',
)

# Establish a connection to the database
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
server = "carserver1.database.windows.net"
database = "cardb"
driver = "{ODBC Driver 18 for SQL Server}"


conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={DB_USERNAME};PWD={DB_PASSWORD}"
connection = pyodbc.connect(conn_str)

# Query all data from the database
query = "SELECT * FROM CARSINFO"
db_df = pd.read_sql(query, connection)

# Close the database connection
connection.close()

# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    # Sidebar
                    html.Div(
                        className='sidebar',
                        children=[
                            html.Div(
                                children=[
                                    # Centered content wrapper
                                    html.Div(
                                        children=[
                                            html.H2("Vehicle Manufacturing Dataset", className="display-4", style={'color': '#555', 'font-size': '24px', 'text-align': 'center'}),
                                            # Centered logo image
                                            html.Div(
                                                children=[
                                                    html.Img(id='brand-logo', style={'width': '80%', 'margin': '0 auto', 'display': 'block'}),
                                                ],
                                                style={'text-align': 'center'},
                                            ),
                                            html.P("Select a car brand from the dropdown menu", style={'color': 'white', 'text-align': 'center'}),
                                            # Navigation buttons
                                            html.Div(
                                                children=[
                                                    dcc.Link("Graphs", href="/graphs", className="btn btn-danger mt-2", style={'width': '100%'}),
                                                    dcc.Link("Tables", href="/tables", className="btn btn-danger mt-2", style={'width': '100%'}),
                                                    dcc.Link("Profile", href="/profile", className="btn btn-primary mt-2", style={'width': '100%'}),  
                                                    dcc.Link("Settings", href="/settings", className="btn btn-outline-primary mt-2", style={'width': '100%'}),  
                                                ],
                                                style={'padding': '1rem', 'background-color': '#101010'},
                                            ),
                                        ],
                                        style={
                                            'padding': '1rem',
                                            'background-color': '#101010',
                                            'minWidth': '200px',
                                        }
                                    ),
                                    # Profile section
                                    html.Div(
                                        children=[
                                            html.Img(src='/assets/images/Tomgomez.png', alt='avatar', className='rounded-circle img-fluid mx-auto d-block', style={'width': '150px'}),
                                            html.H5('Tom Gomez', className='my-3', style={'text-align': 'center', 'color': 'white'}),
                                            html.P('Intern Fall 2023', className='text-white mb-1', style={'text-align': 'center'}),
                                            html.P('Greenville, SC', className='text-white mb-4', style={'text-align': 'center'}),
                                            html.Div(
                                                children=[
                                                    dcc.Link("Profile", href="/profile", className="btn btn-primary"),
                                                    dcc.Link("Settings", href="/settings", className="btn btn-outline-primary ms-1", style={'color': 'white'}),
                                                ],
                                                className="d-flex justify-content-center mb-2"
                                            ),
                                        ],
                                        style={'padding': '1rem', 'background-color': '#101010', 'minWidth': '200px', 'margin-top': '20px'},
                                    ),
                                ],
                            ),
                        ],
                        style={
                            'flex': '0.1',
                            'height': '100%',
                        }
                    ),
                    md=3,
                    sm=12,
                ),
                dbc.Col(
                    # Main content
                    html.Div(
                        [
                            dcc.Location(id='url', refresh=False),
                            html.Div(id='page-content', className='content'),
                        ],
                        style={
                            'flex': '0.9',
                            'padding': '2rem',
                            'background-color': 'black',
                            'height': '100%',
                            'color': 'white',
                        },
                    ),
                    md=9,
                    sm=12,
                ),
            ],
            style={'background-color': 'black'}
        ),
    ],
    fluid=True,
)

# Define the Graphs page content
graphs_page = html.Div([
    html.H1("Vehicle Manufacturing Data Analysis Dashboard", className="display-4", style={'color': 'white', 'font-size': '32px'}),
    dcc.Dropdown(
        id='brand-dropdown',
        options=[
            {'label': 'Chevrolet', 'value': 'Chevrolet'},
            {'label': 'Ford', 'value': 'Ford'},
            {'label': 'Honda', 'value': 'Honda'},
            {'label': 'Hyundai', 'value': 'Hyundai'},
            {'label': 'Toyota', 'value': 'Toyota'}
        ],
        value='Toyota',
        multi=False,
        className='plotly_dark',
        style={'backgroundColor': 'black', 'color': 'black'},
    ),
    dbc.Row([
        dbc.Col(
            dbc.Container(
                dcc.Graph(id='price-vs-mileage-scatter', config={'displayModeBar': True}),
                style={'backgroundColor': '#111', 'border-radius': '15px', 'padding': '10px', 'margin-bottom': '20px'},
            ),
            md=6,
            sm=12,
        ),
        dbc.Col(
            dbc.Container(
                dcc.Graph(id='color-distribution-bar', config={'displayModeBar': True}),
                style={'backgroundColor': '#111', 'border-radius': '15px', 'padding': '10px', 'margin-bottom': '20px'},
            ),
            md=6,
            sm=12,
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Container(
                dcc.Graph(id='model-pie-chart', config={'displayModeBar': True}),
                style={'backgroundColor': '#111', 'border-radius': '15px', 'padding': '10px', 'margin-bottom': '20px'},
            ),
            md=6,
            sm=12,
        ),
        dbc.Col(
            dbc.Container(
                dcc.Graph(id='location-map', figure=map_fig, config={'displayModeBar': True}),
                style={'backgroundColor': '#111', 'border-radius': '15px', 'padding': '10px', 'margin-bottom': '20px'},
            ),
            md=6,
            sm=12,
        ),
    ]),
])

# Define the Tables page content
tables_page = html.Div([
    html.H1("Tables", className="display-4", style={'color': 'white', 'font-size': '32px'}),
    html.Div([
        dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in db_df.columns],
            data=db_df.to_dict('records'),
            style_table={'height': '500px', 'overflowY': 'auto'},
            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
            style_cell={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
        )
    ], style={'height': '500px'}),
])

# Define the Profile page content
profile_page = html.Div([
    html.H1("Profile", className="display-4", style={'color': 'white', 'font-size': '32px'}),
    html.Div([
        html.Img(src='/assets/images/Tomgomez.png', alt='avatar', className='rounded-circle img-fluid mx-auto d-block', style={'width': '150px'}),
        html.H5('Tom Gomez', className='my-3', style={'text-align': 'center', 'color': 'white'}),
        html.P('Intern Fall 2023', className='text-white mb-1', style={'text-align': 'center'}),
        html.P('Greenville, SC', className='text-white mb-4', style={'text-align': 'center'}),
        dbc.Row([
            dbc.Col(html.H6("Full Name"), width=3),
            dbc.Col(dcc.Input(type="text", className="form-control", value="Tom Gomez"), width=9),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.H6("Email"), width=3),
            dbc.Col(dcc.Input(type="text", className="form-control", value="TomGomez@example.com"), width=9),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.H6("Phone"), width=3),
            dbc.Col(dcc.Input(type="text", className="form-control", value="(239) 816-9029"), width=9),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.H6("Postion"), width=3),
            dbc.Col(dcc.Input(type="text", className="form-control", value="Intern Fall 2023"), width=9),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.H6("Address"), width=3),
            dbc.Col(dcc.Input(type="text", className="form-control", value="Greenville, SC"), width=9),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(),  # Empty column to offset the button
            dbc.Col(html.Button(type="button", className="btn btn-primary px-4", children="Save Changes"), width=9),
        ]),
    ], className="col-lg-8", style={'margin': '0 auto'}),
])

# Define the Settings page content (you can add more content here)
settings_page = html.Div([
    html.H1("Settings", className="display-4", style={'color': 'white', 'font-size': '32px'}),
    html.P("This is the Settings page content.", style={'color': 'white'}),
])

# Callback to update the page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/graphs':
        return graphs_page
    elif pathname == '/tables':
        return tables_page
    elif pathname == '/profile':
        return profile_page
    elif pathname == '/settings':
        return settings_page
    else:
        # If the URL is invalid, return a 404 error
        return '404 Page Not Found'

# Callback to update the brand logo based on the selected brand
@app.callback(
    Output('brand-logo', 'src'),
    Input('brand-dropdown', 'value'),
)
def update_brand_logo(selected_brand):
    return get_image_path(selected_brand)

# Callback to update the scatter plot, color distribution bar chart, and model pie chart based on the selected brand
@app.callback(
    [Output('price-vs-mileage-scatter', 'figure'),
     Output('color-distribution-bar', 'figure'),
     Output('model-pie-chart', 'figure')],
    [Input('brand-dropdown', 'value')],
)
def update_plots(selected_brand):
    server = "carserver1.database.windows.net"
    database = "cardb"
    driver = "{ODBC Driver 18 for SQL Server}"

    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    connection = pyodbc.connect(conn_str)

    query = f"SELECT * FROM CARSINFO WHERE Brand = '{selected_brand}'"
    filtered_df = pd.read_sql(query, connection)

    connection.close()

    scatter_fig = px.scatter(
        filtered_df, x='Mileage', y='Price', color='Color',
        title=f'Price vs Mileage for {selected_brand} Cars',
        template='plotly_dark',
    )

    color_distribution = filtered_df['Color'].value_counts().reset_index()
    color_distribution.columns = ['Color', 'Count']
    color_fig = px.bar(
        color_distribution, x='Color', y='Count',
        title=f'Color Distribution for {selected_brand} Cars',
        color='Color',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template='plotly_dark',
    )

    model_distribution = filtered_df['Model'].value_counts().reset_index()
    model_distribution.columns = ['Model', 'Count']
    model_pie_fig = px.pie(
        model_distribution, names='Model', values='Count',
        title=f'Model Distribution for {selected_brand} Cars',
        template='plotly_dark',
    )

    return scatter_fig, color_fig, model_pie_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
