from flask import Flask, render_template, url_for
import requests
import random

app = Flask(__name__)
url = "https://dogapi.dog/api/v2/breeds"

def breeds(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        breeds_list = data.get('data', [])
        if breeds_list:
            return random.choice(breeds_list)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Помилка запиту: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/breeds-dogs')
def bree():
    breed = breeds(url)
    if breed is None:
        return "Помилка: не вдалося отримати дані про породу", 500
    return render_template("breeds.html", bre=breed)

if __name__ == '__main__':
    app.run(debug=True)