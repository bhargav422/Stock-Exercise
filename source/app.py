from flask import Flask
app = Flask(__name__)

@app.route('/Portfolio')
def MyStock():
    return "Get your stock here"

if __name__ == '__main__':
    app.run()