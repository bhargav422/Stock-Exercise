from flask import Flask, render_template, redirect, request, url_for
from source import stocks_list

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/go-to-dash')
def stocks():
    """

    Create a dashbar with a list of stocks
    """
    return redirect('/dash')

dash_app = stocks_list.create_dash_app(app)

if __name__ == "__main__":
    app.run(debug=True)