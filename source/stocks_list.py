from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objects as go

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')
    stock_cache = {}

    dash_app.layout = html.Div([
        html.H1('Real-Time Indian Stock Data'),
        dcc.Input(id='stock-symbol', type='text', placeholder='Enter stock symbol (e.g., RELIANCE.NS)', value='RELIANCE.NS'),
        html.Button('Fetch Data', id='fetch-button', n_clicks=0),
        html.Div(id='stock-data'),
        html.Div(id='output-graph')
    ])

    # Callback to fetch stock data upon button click
    @dash_app.callback(
        [Output('stock-data', 'children'),
         Output('output-graph', 'children')],
        [Input('fetch-button', 'n_clicks')],
        [State('stock-symbol', 'value')]
    )
    def update_stock_data(n_clicks, symbol):
        if n_clicks <= 0:
            return 'Enter a stock symbol and click "Fetch Data".', ''

        symbol = normalize_symbol(symbol)
        if not symbol:
            return 'Enter a valid stock symbol.', ''

        try:
            df = fetch_stock_history(symbol, stock_cache)
        except Exception as e:
            return f"Error retrieving stock data: {str(e)}", ''

        if df.empty or 'Close' not in df:
            return 'Error fetching data or invalid symbol', ''

        latest_data = df.iloc[-1]
        price = latest_data['Close']
        stock_data = f'Symbol: {symbol}, Latest Price: ₹{price:.2f}'
        return stock_data, update_graph(symbol, df)

    def normalize_symbol(symbol):
        return symbol.strip().upper() if symbol else ''

    def fetch_stock_history(symbol, cache):
        if symbol not in cache:
            stock = yf.Ticker(symbol)
            cache[symbol] = stock.history(period="5y")
        return cache[symbol]

    def update_graph(symbol, df):
        if df.empty or 'Close' not in df:
            return html.Div("No historical data available for this symbol.")

        figure = go.Figure(data=[
            go.Scatter(x=df.index, y=df['Close'], mode='lines', name=symbol)
        ])

        figure.update_layout(title=f"{symbol} Stock Price Over Time")
        return dcc.Graph(id='stock-graph', figure=figure)

    return dash_app
