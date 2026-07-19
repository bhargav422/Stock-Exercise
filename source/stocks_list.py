import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, ALL, State
import json
import yfinance as yf
import datetime
import plotly.graph_objects as go
import pandas as pd

STOCK_CATEGORIES = {
    'Banking & Finance': {
        'display_names': ['Reliance', 'TCS', 'Infosys', 'HDFC', 'ICICI Bank', 'Wipro', 'L&T', 'Maruti'],
        'symbols': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS', 'WIPRO.NS', 'LT.NS', 'MARUTI.NS']
    },
    'IT Stocks': {
        'display_names': ['HCL', 'Happiest Mind'],
        'symbols': ['HCLTECH.NS', 'HAPPIEST.NS']
    },
    'Metal Stocks': {
        'display_names': ['Hindustan Copper', 'Silver Bees'],
        'symbols': ['HINDALCO.NS', 'SILVERBEES.NS']
    },
    'Pharma Stocks': {
        'display_names': ['Sun Pharma'],
        'symbols': ['SUNPHARMA.NS']
    },
    'PSU Stocks': {
        'display_names': ['RVNL', 'IRCTC'],
        'symbols': ['RVNL.NS', 'IRCTC.NS']
    }
}

POPULAR_STOCKS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS', 'WIPRO.NS', 'LT.NS', 'MARUTI.NS']

def normalize_name(value):
    """Normalize text for reliable comparisons."""
    return ' '.join(str(value).strip().lower().split())


def get_all_categories(categories_data=None):
    """Combine the default stock categories with any user-added custom categories."""
    merged = {}
    for category, data in STOCK_CATEGORIES.items():
        merged[category] = {
            'display_names': list(data['display_names']),
            'symbols': list(data['symbols'])
        }

    if categories_data:
        for category, data in categories_data.items():
            if category not in merged:
                merged[category] = {'display_names': [], 'symbols': []}
            merged[category]['display_names'].extend(data.get('display_names', []))
            merged[category]['symbols'].extend(data.get('symbols', []))

    return merged


def resolve_stock_symbol(display_name, categories_data=None):
    """Resolve a display name to a stock symbol using saved data or Yahoo Finance."""
    if not display_name:
        return None

    value = str(display_name).strip()
    if not value:
        return None

    if value.upper() == value or '.' in value or value.endswith(('.NS', '.BO', '.NSE', '.BSE')):
        return value

    target_name = normalize_name(value)
    for _, data in get_all_categories(categories_data).items():
        for idx, name in enumerate(data['display_names']):
            if normalize_name(name) == target_name:
                return data['symbols'][idx]

    try:
        search_result = yf.search(value, max_results=1)
        if isinstance(search_result, dict):
            quotes = search_result.get('quotes') or []
            if quotes:
                return quotes[0].get('symbol')
    except Exception:
        pass

    try:
        info = yf.Ticker(value).info
        if isinstance(info, dict) and info.get('symbol'):
            return info['symbol']
    except Exception:
        pass

    return value


def get_category_buttons(category, categories_data=None):
    """Create stock buttons for a given category. Use categories_data when provided."""
    data = categories_data.get(category) if categories_data is not None else STOCK_CATEGORIES[category]
    buttons = []
    for display_name, symbol in zip(data['display_names'], data['symbols']):
        buttons.append(
            html.Button(
                display_name,
                id={'type': 'stock-btn', 'index': symbol},
                n_clicks=0,
                style={
                    'padding': '12px 15px',
                    'margin': '8px 0',
                    'cursor': 'pointer',
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'transition': 'all 0.3s ease',
                    'width': '100%',
                    'textAlign': 'left',
                    'boxShadow': '0 4px 15px rgba(102, 126, 234, 0.4)'
                },
                className='stock-btn'
            )
        )
    return html.Div(buttons, style={'display': 'flex', 'flexDirection': 'column', 'gap': '5px'})

def get_stock_figure(symbol):
    """Fetch stock data and create a Plotly figure"""
    try:
        stock = yf.Ticker(symbol)
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime.now()
        df = stock.history(start=start, end=end)
        
        if df.empty:
            return go.Figure().add_annotation(text=f"No data available for {symbol}"), "N/A"
        
        # Get latest valid price (skip NaN values)
        latest_price = df['Close'].iloc[-1]
        if pd.isna(latest_price):
            # Find the last non-NaN price
            valid_prices = df['Close'].dropna()
            if valid_prices.empty:
                return go.Figure().add_annotation(text=f"No valid price data for {symbol}"), "N/A"
            latest_price = valid_prices.iloc[-1]
        
        # Remove rows with NaN in Close price for cleaner graph
        df_clean = df.dropna(subset=['Close']).copy()
        
        if df_clean.empty:
            return go.Figure().add_annotation(text=f"No valid price data for {symbol}"), "N/A"
        
        figure = go.Figure(data=[
            go.Scatter(x=df_clean.index, y=df_clean['Close'], mode='lines', name=symbol, fill='tozeroy')
        ])
        figure.update_layout(
            title=f"{symbol} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            hovermode='x unified',
            height=600,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return figure, f"₹{latest_price:.2f}"
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Error: {str(e)[:100]}")
        return empty_fig, "Error"

def get_display_name(symbol, categories_data=None):
    """Convert stock symbol to display name."""
    for _, data in get_all_categories(categories_data).items():
        if symbol in data['symbols']:
            idx = data['symbols'].index(symbol)
            return data['display_names'][idx]
    return symbol

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')
    stock_cache = {}
    initial_category = next(iter(STOCK_CATEGORIES))

    # Get initial graph for RELIANCE.NS
    initial_fig, initial_price = get_stock_figure('RELIANCE.NS')

    dash_app.layout = html.Div([
        dcc.Store(id='categories-store', data=STOCK_CATEGORIES),
        # Header with stock info
        html.Div([
            html.H2('Reliance', id='stock-symbol-display', style={'display': 'inline-block', 'marginRight': '20px', 'margin': '10px 0'}),
            html.Span(initial_price, id='stock-price', style={'fontSize': '24px', 'color': '#28a745', 'fontWeight': 'bold'})
        ], style={'padding': '20px', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
        
        # Main container
        html.Div([
            # Left side - Category tabs and stock buttons
            html.Div(
                [
                    html.H4('Categories', style={'marginBottom': '10px', 'color': '#333', 'fontSize': '14px', 'fontWeight': 'bold'}),
                    dcc.Tabs(
                        id='category-tabs',
                        value=initial_category,
                        children=[
                            dcc.Tab(
                                label=html.Span([
                                    html.Span(
                                        {
                                            'Banking & Finance': '🏦',
                                            'IT Stocks': '💻',
                                            'Metal Stocks': '⛏️',
                                            'Pharma Stocks': '💊',
                                            'PSU Stocks': '🏛️'
                                        }.get(category, '📌'),
                                        style={'marginRight': '6px'}
                                    ),
                                    html.Span(category, style={'whiteSpace': 'nowrap', 'overflow': 'hidden', 'textOverflow': 'ellipsis'})
                                ], style={'display': 'inline-flex', 'alignItems': 'center', 'maxWidth': '100%', 'overflow': 'hidden'}),
                                value=category,
                                style={
                                    'padding': '10px 16px',
                                    'border': '1px solid #d8def6',
                                    'borderRadius': '999px',
                                    'marginRight': '10px',
                                    'marginBottom': '8px',
                                    'backgroundColor': '#ffffff',
                                    'color': '#374151',
                                    'fontWeight': '600',
                                    'boxShadow': '0 2px 6px rgba(0,0,0,0.06)',
                                    'maxWidth': '100%',
                                    'whiteSpace': 'nowrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis'
                                },
                                selected_style={
                                    'padding': '10px 16px',
                                    'backgroundColor': '#4f46e5',
                                    'color': '#ffffff',
                                    'border': '1px solid #4338ca',
                                    'borderRadius': '999px',
                                    'boxShadow': '0 4px 12px rgba(79, 70, 229, 0.25)',
                                    'maxWidth': '100%',
                                    'whiteSpace': 'nowrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis'
                                }
                            )
                            for category in STOCK_CATEGORIES.keys()
                        ],
                        style={'marginBottom': '10px', 'display': 'flex', 'flexWrap': 'wrap'}
                    ),
                    html.Div(id='category-content', children=get_category_buttons(initial_category), style={'paddingTop': '5px'}),
                    html.Div([
                        html.Div([
                            html.Label('Add a stock by display name', style={'fontSize': '12px', 'fontWeight': '600', 'color': '#4b5563', 'display': 'block', 'marginBottom': '6px'}),
                            dcc.Input(id='stock-name-input', type='text', placeholder='e.g. Reliance or Infosys', style={'width': '100%', 'marginBottom': '8px', 'padding': '8px', 'boxSizing': 'border-box'}),
                            html.Button('➕ Add Stock', id='add-stock', n_clicks=0, style={'width': '100%', 'padding': '10px', 'background': 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': '600'})
                        ], style={'marginTop': '12px'})
                    ], style={'paddingTop': '8px'})
                ],
                style={
                    'width': '25%',
                    'padding': '15px',
                    'overflowY': 'auto',
                    'borderRight': '2px solid #ddd',
                    'boxSizing': 'border-box',
                    'height': 'calc(100vh - 100px)'
                }
            ),
            
            # Right side - Graph
            html.Div([
                dcc.Graph(id='stock-graph', figure=initial_fig, style={'height': 'calc(100vh - 100px)'})
            ], style={
                'width': '75%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'boxSizing': 'border-box',
                'padding': '0'
            })
        ], style={'display': 'flex', 'width': '100%'})
    ])

    @dash_app.callback(
        Output('category-content', 'children'),
        Input('category-tabs', 'value'),
        Input('categories-store', 'data')
    )
    def update_category_content(selected_category, categories_data):
        if selected_category not in (categories_data or {}):
            selected_category = initial_category
        return get_category_buttons(selected_category, categories_data)

    @dash_app.callback(
        [Output('categories-store', 'data'), Output('category-content', 'children')],
        Input('add-stock', 'n_clicks'),
        State('stock-name-input', 'value'),
        State('category-tabs', 'value'),
        State('categories-store', 'data')
    )
    def add_stock(n_clicks, display_name, selected_category, categories_data):
        if not n_clicks:
            return categories_data, get_category_buttons(selected_category, categories_data)

        if not display_name:
            return categories_data, get_category_buttons(selected_category, categories_data)

        resolved_symbol = resolve_stock_symbol(display_name, categories_data)
        if not resolved_symbol:
            return categories_data, get_category_buttons(selected_category, categories_data)

        categories_data = categories_data or {}
        category = categories_data.get(selected_category)
        if category is None:
            categories_data[selected_category] = {'display_names': [display_name], 'symbols': [resolved_symbol]}
        else:
            category['display_names'].append(display_name)
            category['symbols'].append(resolved_symbol)

        return categories_data, get_category_buttons(selected_category, categories_data)

    # Callback to update graph when stock button is clicked
    @dash_app.callback(
        [Output('stock-graph', 'figure'),
         Output('stock-price', 'children'),
         Output('stock-symbol-display', 'children')],
        Input({'type': 'stock-btn', 'index': ALL}, 'n_clicks'),
        State('categories-store', 'data'),
        prevent_initial_call=True
    )
    def update_on_stock_click(n_clicks, categories_data):
        if not n_clicks or sum(n_clicks) == 0:
            return initial_fig, initial_price, 'Reliance'
        
        # Find which button was clicked
        ctx = dash.callback_context
        if not ctx.triggered:
            return initial_fig, initial_price, 'Reliance'
        
        # Use triggered_id to get the pattern-matching ID directly
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            return initial_fig, initial_price, 'Reliance'
        
        # Extract the symbol from the triggered ID (it's a dict from pattern-matching)
        symbol = triggered_id.get('index', 'RELIANCE.NS')
        
        # Get stock data and create graph
        figure, price = get_stock_figure(symbol)
        display_name = get_display_name(symbol, categories_data)
        
        return figure, price, display_name

    return dash_app