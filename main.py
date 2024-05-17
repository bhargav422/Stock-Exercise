from flask import Flask, render_template, redirect, request, url_for


app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/Stocks', methods = ["POST", "GET"])
def stocks():
    """

    Create a dashbar with a list of stocks
    """


if __name__ == "__main__":
    app.run(debug=True)