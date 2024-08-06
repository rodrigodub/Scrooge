# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'
#
#
# if __name__ == '__main__':
#     app.run()

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for the pie chart
labels = ['Apples', 'Bananas', 'Cherries', 'Dates', 'Elderberries']
values = [4500, 2500, 1050, 550, 200]

# Create a pie chart using Plotly
fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Interactive Pie Chart", className='text-center text-primary mb-4'), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='pie-chart', figure=fig), width=12)
    ])
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
