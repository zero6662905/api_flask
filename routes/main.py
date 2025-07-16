from flask import render_template
from flask_login import login_required
from app import app

from flask_login import current_user
from settings import cache


@app.route("/")
@app.route("/home")
@cache.cached(timeout=20)
def index():    
    try:
        return render_template("index.html", username = current_user.username)
    except AttributeError: 
        return render_template("index.html", username = "Anonim")
