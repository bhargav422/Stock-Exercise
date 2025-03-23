from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import yfinance as yf
import datetime
import plotly.graph_objects as go
import os
from flask import send_from_directory

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')

    dash_app.layout = html.Div([
        html.H1('Real-Time Indian Stock Data'),
        html.Link(rel='stylesheet', href='./templates/dashboard_style.css'),
        dcc.Input(id='stock-symbol', type='text', placeholder='Enter stock symbol (e.g., RELIANCE.NS)', value='RELIANCE.NS'),
        html.Button('Fetch Data', id='fetch-button', n_clicks=0),
        html.Div(id='stock-data'),
        html.Div(id='output-graph')
    ])

    # Serve CSS file from a different directory
    @flask_app.route('/static/css/<path:path>')
    def serve_css(path):
        return send_from_directory(os.path.join(os.getcwd(), 'static', 'css'), path)

    # Callback to fetch stock data upon button click
    @dash_app.callback(
        [Output('stock-data', 'children'),
         Output('output-graph', 'children')],
        [Input('fetch-button', 'n_clicks')],
        [State('stock-symbol', 'value')]
    )
    def update_stock_data(n_clicks, symbol):
        if n_clicks > 0:
            # Fetch stock data using yfinance
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d", interval="1m")
            if not hist.empty:
                latest_data = hist.iloc[-1]
                price = latest_data['Close']
                stock_data = f'Symbol: {symbol}, Latest Price: ₹{price}'
                
                # Update graph
                graph = update_graph(symbol)
                
                return stock_data, graph
            else:
                return 'Error fetching data or invalid symbol', ''
        return 'Enter a stock symbol and click "Fetch Data".', ''

    def update_graph(symbol):
        start = datetime.datetime(2010, 1, 1)
        end = datetime.datetime.now()
    
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start, end=end)
    
            figure = go.Figure(data=[
                go.Scatter(x=df.index, y=df['Close'], mode='lines', name=symbol)
            ])
    
            figure.update_layout(title=f"{symbol} Stock Price Over Time")
            graph = dcc.Graph(id='stock-graph', figure=figure)
        except Exception as e:
            graph = html.Div(f"Error retrieving stock data: {str(e)}")
        
        return graph

    return dash_app