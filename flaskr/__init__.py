import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

DB_NAME = 'data.sqlite'

login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, DB_NAME)
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    from flaskr.routes import bp
    app.register_blueprint(bp) #blueprintを追加
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    return app

