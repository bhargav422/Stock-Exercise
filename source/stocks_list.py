from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import yfinance as yf



def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')

    dash_app.layout = html.Div([
        html.H1('Real-Time Indian Stock Data'),
        dcc.Input(id='stock-symbol', type='text', placeholder='Enter stock symbol (e.g., RELIANCE.NS)', value='RELIANCE.NS'),
        html.Button('Fetch Data', id='fetch-button', n_clicks=0),
        html.Div(id='stock-data')
        ])


    # Callback to fetch stock data upon button click
    @dash_app.callback(
        Output('stock-data', 'children'),
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
                return f'Symbol: {symbol}, Latest Price: ₹{price}'
            else:
                return 'Error fetching data or invalid symbol'
        return 'Enter a stock symbol and click "Fetch Data".'
    
    return dash_app