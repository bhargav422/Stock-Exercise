import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import yfinance as yf


class StockData:
    def __init__(self, flask_base):
        self.app = dash.Dash(__name__, server=flask_base, url_base_pathname='/my_stocks/')
        self.stocks = {}
        self.stock_data = {}
        self.app.title = "Stock Watchlist"

    def create_watchlist(self):
        self.app.layout = html.Div([
            html.H1('Stock Watchlist'),
            dcc.Input(id='stock-symbol', type='text', placeholder='Enter stock symbol (e.g., RELIANCE.NS)'),
            html.Button('Add to Watchlist', id='add-button', n_clicks=0),
            html.Div(id='watchlist'),
            dcc.Graph(id='stock-graph')
        ])

        @self.app.callback(
            Output('watchlist', 'children'),
            Output('stock-graph', 'figure'),
            Input('add-button', 'n_clicks'),
            State('stock-symbol', 'value')
        )
        def update_watchlist(n_clicks, symbol):
            symbol = self.normalize_symbol(symbol)
            if n_clicks > 0 and symbol:
                self.stocks[symbol] = symbol
                self.stock_data[symbol] = self.get_stock_data(symbol)
                return self.create_watchlist_display(), self.create_graph(symbol)
            return self.create_watchlist_display(), {}
        return self.app.server

    def normalize_symbol(self, symbol):
        return symbol.strip().upper() if symbol else ''

    def create_watchlist_display(self):
        if not self.stocks:
            return "No stocks in watchlist."
        return html.Ul([html.Li(stock) for stock in self.stocks.keys()])

    def create_graph(self, symbol): 
        if symbol in self.stock_data:
            data = self.stock_data[symbol]
            if data.empty or 'Close' not in data:
                return {}
            figure = {
                'data': [
                    {'x': data.index, 'y': data['Close'], 'type': 'line', 'name': symbol}
                ],
                'layout': {
                    'title': f"{symbol} Stock Price Over Time"
                }
            }
            return figure
        return {}

    def get_stock_data(self, symbol):
        if symbol not in self.stock_data:
            self.stock_data[symbol] = yf.Ticker(symbol).history(period="1y")
        return self.stock_data[symbol]


if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    stock_data = StockData(app)
    stock_data.create_watchlist()
    app.run(debug=True)
