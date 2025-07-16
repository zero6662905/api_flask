from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from models import Users
from settings import Config, cache

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

cache.init_app(app)


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "NEED LOGIN"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = Users.get(user_id)
    print(user)
    return user

from routes.main import *
from routes.users import *
from routes.messager import *
    
    
if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, port=5050)
