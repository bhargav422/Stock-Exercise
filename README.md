# Stock-Exercise

A Flask and Dash stock dashboard for looking up Indian stock symbols, plotting recent price history, and keeping a simple in-memory watchlist.

## Features

- Flask homepage at `/`
- Dash stock dashboard at `/dash/`
- Dash watchlist at `/my_stocks/`
- Yahoo Finance data via `yfinance`
- Basic machine-learning scripts in `src/` for building target/features and training a random forest classifier

## Requirements

- Python 3.9+
- Internet access for Yahoo Finance data
- Stock symbols in Yahoo Finance format, for example `RELIANCE.NS`, `TCS.NS`, or `INFY.NS`

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open the app at:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/dash/`
- `http://127.0.0.1:5000/my_stocks/`

## Run With Docker

```bash
docker build -t my-flask-dash-app .
docker run -p 5000:80 my-flask-dash-app
```

The container runs Gunicorn on port `80`, so the command above maps it to local port `5000`.

## ML Scripts

Run the model training script from the project root:

```bash
python3 -m src.ml_data
```

When prompted, enter a Yahoo Finance symbol such as `RELIANCE.NS`.

## Project Structure

- `app.py` - Flask entrypoint and Dash app registration
- `source/stocks_list.py` - main stock lookup dashboard
- `source/get_stocks.py` - watchlist dashboard
- `src/predict_price.py` - historical data and feature creation
- `src/ml_data.py` - random forest training and evaluation
- `templates/` - Flask homepage templates
- `static/` - static assets

## Known Limitations

- Watchlist data is stored in memory and resets when the server restarts.
- Stock data is cached in memory per process only.
- Yahoo Finance requests can fail or be rate-limited.
- There is no persistent database or user authentication.
- Automated tests are not yet included.

## Basic Verification

```bash
python3 -m compileall app.py source src
```
