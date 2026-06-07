import yfinance as yf

def get_stock_data(ticker, start="2020-01-01", end="2025-01-01"):
    df = yf.download(ticker, start=start, end=end)

    df = df[["Open", "High", "Low", "Close", "Volume"]]

    # Create the "target": 1 if tomorrow's close is higher than today's, else 0
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    df['Return_1D'] = df['Close'].pct_change()
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['Volume_Change'] = df['Volume'].pct_change()

    df = df.dropna()
    return df

if __name__ == '__main__':
    ticker = input("Enter stock name: ")
    print(get_stock_data(ticker).tail())
