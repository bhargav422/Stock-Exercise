from flask import Flask, render_template, redirect
from source import stocks_list
from source import get_stocks

app = Flask(__name__)
dash_app = stocks_list.create_dash_app(app)
watchlist_app = get_stocks.StockData(app)
watchlist_app.create_watchlist()


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/check_stocks')
def check_stocks():

    return redirect('/dash')

@app.route('/watchlist')
def watchlist():
    """

    Create a dashbar with a list of stocks
    """
    stock_data = get_stocks.StockData(app)
    stock_data.create_watchlist()
    return redirect('/my_stocks')


if __name__ == "__main__":
    app.run(debug=True, port=5001)
