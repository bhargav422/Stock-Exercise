import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, ALL
import json
import yfinance as yf
import datetime
import plotly.graph_objects as go

POPULAR_STOCKS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS', 'WIPRO.NS', 'LT.NS', 'MARUTI.NS']

def get_stock_figure(symbol):
    """Fetch stock data and create a Plotly figure"""
    try:
        stock = yf.Ticker(symbol)
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime.now()
        df = stock.history(start=start, end=end)
        
        if df.empty:
            return go.Figure().add_annotation(text=f"No data available for {symbol}"), "N/A"
        
        # Get latest price
        latest_price = df['Close'].iloc[-1]
        
        figure = go.Figure(data=[
            go.Scatter(x=df.index, y=df['Close'], mode='lines', name=symbol, fill='tozeroy')
        ])
        figure.update_layout(
            title=f"{symbol} Stock Price (Last 12 Months)",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            hovermode='x unified',
            height=600,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return figure, f"₹{latest_price:.2f}"
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Error: {str(e)}")
        return empty_fig, "Error"

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')

    # Create stock buttons
    stock_buttons = [
        html.Button(
            stock,
            id={'type': 'stock-btn', 'index': stock},
            n_clicks=0,
            style={
                'padding': '12px 15px',
                'margin': '5px 0',
                'cursor': 'pointer',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'transition': 'all 0.3s',
                'width': '100%',
                'textAlign': 'left'
            },
            className='stock-btn'
        )
        for stock in POPULAR_STOCKS
    ]

    # Get initial graph for RELIANCE.NS
    initial_fig, initial_price = get_stock_figure('RELIANCE.NS')

    dash_app.layout = html.Div([
        html.Div([
            # Left side - Stock list
            html.Div([
                html.H2('Popular Stocks', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#333'}),
                html.Div(stock_buttons, style={'display': 'flex', 'flexDirection': 'column', 'gap': '5px'})
            ], style={
                'width': '18%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '20px',
                'borderRight': '2px solid #ddd',
                'overflowY': 'auto',
                'height': '90vh',
                'boxSizing': 'border-box'
            }),
            
            # Right side - Graph and Info
            html.Div([
                html.Div([
                    html.H2('RELIANCE.NS', id='stock-symbol-display', style={'display': 'inline-block', 'marginRight': '20px'}),
                    html.Span(initial_price, id='stock-price', style={'fontSize': '24px', 'color': '#28a745', 'fontWeight': 'bold'})
                ], style={'marginBottom': '20px', 'borderBottom': '1px solid #ddd', 'paddingBottom': '15px'}),
                dcc.Graph(id='stock-graph', figure=initial_fig, style={'height': '85vh'})
            ], style={
                'width': '82%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '20px',
                'boxSizing': 'border-box'
            })
        ], style={'display': 'flex', 'width': '100%', 'height': '100vh'})
    ])

    # Callback to update graph when stock button is clicked
    @dash_app.callback(
        [Output('stock-graph', 'figure'),
         Output('stock-price', 'children'),
         Output('stock-symbol-display', 'children')],
        Input({'type': 'stock-btn', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def update_on_stock_click(n_clicks):
        if not n_clicks or sum(n_clicks) == 0:
            return initial_fig, initial_price, 'RELIANCE.NS'
        
        # Find which button was clicked
        ctx = dash.callback_context
        if not ctx.triggered:
            return initial_fig, initial_price, 'RELIANCE.NS'
        
        # Extract the stock symbol from the triggered button
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_data = json.loads(button_id)
        symbol = button_data['index']
        
        # Get stock data and create graph
        figure, price = get_stock_figure(symbol)
        
        return figure, price, symbol

    return dash_app