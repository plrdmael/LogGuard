import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import subprocess

# Lire les données depuis le fichier CSV
def load_error_logs(path_to_file):
    try:
        df = pd.read_csv(path_to_file)
        return df
    except Exception as e:
        print(f"Error loading {path_to_file}: {e}")
        return pd.DataFrame()

def load_access_logs(path_to_file):
    try:
        df = pd.read_csv(path_to_file)
        return df
    except Exception as e:
        print(f"Error loading {path_to_file}: {e}")
        return pd.DataFrame()

# Visualization for error logs
def create_error_logs_graph(df_errors):
    if df_errors.empty:
        return go.Figure(), go.Figure()
    fig_ip = px.histogram(df_errors, x="RemoteAddress", title="Error Logs by IP Address")
    fig_attack = px.histogram(df_errors, x="Types d'Attaque", title="Number of alerts raised by type of attack")
    return fig_ip, fig_attack

# Fonction pour créer un graphique des logs d'accès par adresse IP
def create_access_logs_graph(df_access):
    if df_access.empty:
        return go.Figure(), 0
    fig_ip = px.histogram(df_access, x="RemoteAddress", title="Access Logs by IP Address")
    return fig_ip, len(df_access)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Navbar with the new button
navbar = dbc.NavbarSimple(
    brand="Log Visualizer",
    brand_href="#",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Logs Overview", href="/overview")),
        dbc.NavItem(dbc.NavLink("Error Logs", href="/error-logs")),
        dbc.NavItem(dbc.NavLink("Access Logs", href="/access-logs")),
        dbc.NavItem(dbc.NavLink("Server Settings", href="/server-settings")),  # New settings page
        dbc.Button("Refresh", id="refresh-button", color="secondary", className="ml-2"),  # New button
    ],
)

# Content for different pages
home_page = html.Div([
    html.H2("Welcome to Log Visualizer"),
    html.P("Select a page from the menu to view logs."),
])

overview_page = html.Div([
    html.H2("Logs Overview"),
    dbc.Row([
        dbc.Col([
            html.H4("Total Logs"),
            html.P(id="total-logs-count"),
        ]),
        dbc.Col([
            html.H4("Logs Breakdown"),
            dcc.Graph(id="logs-breakdown-pie"),
        ]),
        dbc.Col([
            html.H4("Top IP Addresses"),
            dash_table.DataTable(id="top-ip-addresses-table",
                                 columns=[{"name": "IP Address", "id": "ip"}, {"name": "Count", "id": "count"}],
                                 data=[],
                                 style_table={'overflowX': 'auto'})
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="logs-over-time")
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="heatmap-logs-per-hour"),
        ]),
        dbc.Col([
            dcc.Graph(id="error-vs-access-logs"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("Recent Alerts"),
            dash_table.DataTable(id="recent-alerts-table",
                                 columns=[{"name": "Alert Type", "id": "alert_type"}, {"name": "Details", "id": "details"}],
                                 data=[],
                                 style_table={'overflowX': 'auto'})
        ]),
    ]),
])


error_logs_page = html.Div([
    html.H2("Error Logs"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Filtrer par adresse IP:"),
            dbc.Input(id="filter-ip-error", placeholder="Entrer une adresse IP ou début d'adresse"),
        ]),
        dbc.Col([
            dbc.Label("Nombre minimum de logs:"),
            dbc.Input(id="filter-log-count-min-error", type="number", placeholder="Min", value=0),
        ]),
        dbc.Col([
            dbc.Label("Nombre maximum de logs:"),
            dbc.Input(id="filter-log-count-max-error", type="number", placeholder="Max", value=1000),
        ])
    ]),
    html.Div(id='error-logs-alerts-count'),
    dcc.Graph(id='error-logs-graph'),
    dcc.Graph(id='error-logs-type-attacks'),
    html.H4("Logs Details"),
    dash_table.DataTable(
        id='error-logs-details',
        columns=[],  # Colonnes dynamiques
        data=[],
        style_table={'overflowX': 'auto'}
    )
])

access_logs_page = html.Div([
    html.H2("Access Logs"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Filtrer par adresse IP:"),
            dbc.Input(id="filter-ip-access", placeholder="Entrer une adresse IP ou début d'adresse"),
        ]),
        dbc.Col([
            dbc.Label("Nombre minimum de logs:"),
            dbc.Input(id="filter-log-count-min-access", type="number", placeholder="Min", value=0),
        ]),
        dbc.Col([
            dbc.Label("Nombre maximum de logs:"),
            dbc.Input(id="filter-log-count-max-access", type="number", placeholder="Max", value=1000),
        ])
    ]),
    html.Div(id='access-logs-alerts-count'),
    dcc.Graph(id='access-logs-graph'),
    html.H4("Logs Details"),
    dash_table.DataTable(
        id='access-logs-details',
        columns=[],  # Colonnes dynamiques
        data=[],
        style_table={'overflowX': 'auto'}
    )
])


# New server settings page
server_settings_page = html.Div([
    html.H2("Server Settings"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Server Addresses"),
                dbc.Input(id="server-addresses-input", placeholder="Enter server addresses separated by commas"),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label("IP Whitelist"),
                dbc.Input(id="ip-whitelist-input", placeholder="Enter IP addresses to whitelist separated by commas"),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label("File Save Path"),
                dbc.Input(id="file-save-path-input", placeholder="Enter the path to save files"),
            ])
        ]),
        dbc.Button("Save Settings", id="save-settings-button", color="primary"),
    ]),
    html.Div(id="settings-feedback", className="mt-3")
])

content = html.Div(id="page-content")

# Layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    dbc.Container(content, className="mt-4"),
    dcc.Store(id='error-logs-data'),
    dcc.Store(id='access-logs-data'),
    dcc.Store(id='server-settings-data'),  # Store for server settings
    # dcc.Interval(
    #     id='interval-component',
    #     interval=5*1000,  # Interval in milliseconds (e.g., 60000 for 1 minute)
    #     n_intervals=0
    # )
])

# Callback to update page content
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/overview":
        return overview_page
    elif pathname == "/error-logs":
        return error_logs_page
    elif pathname == "/access-logs":
        return access_logs_page
    elif pathname == "/server-settings":
        return server_settings_page
    else:
        return home_page

# Callback pour charger les données et les stocker dans dcc.Store
@app.callback(
    [Output('error-logs-data', 'data'),
     Output('access-logs-data', 'data')],
    [Input('refresh-button', 'n_clicks')]
)
def load_data(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate  # Empêche la mise à jour au chargement initial

    print("Loading data...")  # Déclaration de débogage
    error_logs = load_error_logs('Ressources/Result/logs_nginx_sorted.csv')
    access_logs = load_access_logs('Ressources/Normalized/data.csv')
    print(f"Loaded {len(error_logs)} error logs and {len(access_logs)} access logs.")  # Déclaration de débogage
    return error_logs.to_dict('records'), access_logs.to_dict('records')


# Callback to update error logs page
@app.callback(
    [Output('error-logs-graph', 'figure'),
     Output('error-logs-type-attacks', 'figure'),
     Output('error-logs-alerts-count', 'children')],
    [Input('error-logs-data', 'data'),
     Input('filter-ip-error', 'value'),
     Input('filter-log-count-min-error', 'value'),
     Input('filter-log-count-max-error', 'value')]
)
def update_error_logs_page(error_logs_data, ip_filter, log_count_min, log_count_max):
    if not error_logs_data:
        return go.Figure(), go.Figure(), "No alerts detected."

    df_errors = pd.DataFrame(error_logs_data)

    # Filtrer par adresse IP
    if ip_filter:
        df_errors = df_errors[df_errors['RemoteAddress'].str.startswith('"'+ip_filter)]

    # Filtrer par nombre de logs
    df_errors = df_errors[df_errors.groupby('RemoteAddress')['RemoteAddress'].transform('count').between(log_count_min, log_count_max)]

    fig_ip, fig_attack = create_error_logs_graph(df_errors)
    nb_alerts = len(df_errors)
    return fig_ip, fig_attack, f"{nb_alerts} alerts detected."


# Callback to update access logs page
@app.callback(
    [Output('access-logs-graph', 'figure'),
     Output('access-logs-alerts-count', 'children')],
    [Input('access-logs-data', 'data'),
     Input('filter-ip-access', 'value'),
     Input('filter-log-count-min-access', 'value'),
     Input('filter-log-count-max-access', 'value')]
)
def update_access_logs_page(access_logs_data, ip_filter, log_count_min, log_count_max):
    if not access_logs_data:
        return go.Figure(), "No logs to display."

    df_access = pd.DataFrame(access_logs_data)

    # Filtrer par adresse IP
    if ip_filter:
        df_access = df_access[df_access['RemoteAddress'].str.startswith('"'+ip_filter)]

    # Filtrer par nombre de logs
    df_access = df_access[df_access.groupby('RemoteAddress')['RemoteAddress'].transform('count').between(log_count_min, log_count_max)]

    fig_ip, num_logs = create_access_logs_graph(df_access)
    return fig_ip, f"{num_logs} logs analyzed."


# Callback to update the logs details table based on histogram click
@app.callback(
    [Output('error-logs-details', 'data'),
     Output('error-logs-details', 'columns')],
    [Input('error-logs-graph', 'clickData'),
     State('error-logs-data', 'data')]
)
def display_log_details(clickData, error_logs_data):
    print("Displaying log details...")  # Debugging statement
    if clickData is None or not error_logs_data:
        return [], []

    df_errors = pd.DataFrame(error_logs_data)
    clicked_ip = clickData['points'][0]['x']
    filtered_df = df_errors[df_errors['RemoteAddress'] == clicked_ip]
    
    columns = [{'name': col, 'id': col} for col in filtered_df.columns]
    data = filtered_df.to_dict('records')
    
    return data, columns

@app.callback(
    [Output('access-logs-details', 'data'),
     Output('access-logs-details', 'columns')],
    [Input('access-logs-graph', 'clickData'),
     State('access-logs-data', 'data')]
)
def display_log_details(clickData, access_logs_data):
    print("Displaying log details...")  # Debugging statement
    if clickData is None or not access_logs_data:
        return [], []

    df_errors = pd.DataFrame(access_logs_data)
    clicked_ip = clickData['points'][0]['x']
    filtered_df = df_errors[df_errors['RemoteAddress'] == clicked_ip]
    
    columns = [{'name': col, 'id': col} for col in filtered_df.columns]
    data = filtered_df.to_dict('records')
    
    return data, columns

# Callback to save server settings
@app.callback(
    Output("settings-feedback", "children"),
    [Input("save-settings-button", "n_clicks")],
    [State("server-addresses-input", "value"),
     State("ip-whitelist-input", "value"),
     State("file-save-path-input", "value"),
     State("server-settings-data", "data")]
)
def save_server_settings(n_clicks, server_addresses, ip_whitelist, file_save_path, current_settings):
    if n_clicks is None:
        return ""

    new_settings = {
        "server_addresses": server_addresses,
        "ip_whitelist": ip_whitelist,
        "file_save_path": file_save_path
    }

    return "Settings saved successfully!"


if __name__ == "__main__":
    app.run_server(debug=True)
