import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flaskr.utils.template_filters import replace_newline, time_print, message_view_length

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
    app.config['SECRET_KEY'] = b'\xb2\x19`\x9a\x02V\xfdG\xe5\x90\x0c\xde\x19H\xaei\x9b7d\xe5\xab9\x0e\xae'
    #app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, DB_NAME)
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    from flaskr.routes import bp
    app.register_blueprint(bp) #blueprintを追加
    app.add_template_filter(replace_newline)
    app.add_template_filter(time_print)
    app.add_template_filter(message_view_length)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    return app

