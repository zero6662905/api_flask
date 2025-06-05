from flask import Flask, render_template, url_for
import requests

app = Flask(__name__)
url = "https://api.coindesk.com/v1/bpi/currentprice.json"


def bpi(url):
    response = requests.get(url)
    return response.json

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crypto')
def crypto():
    kurs = bpi(url)
    return kurs

if __name__ == '__main__':
    app.run(debug=True)