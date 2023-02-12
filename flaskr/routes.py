from flask import ( 
    Blueprint, render_template, redirect, request, url_for, session
)
from flask_login import login_user, logout_user, login_required
from dotenv import load_dotenv

from flaskr.forms import LoginForm, RegisterForm, AuthForm
from flaskr.models import User, Auth
from flaskr import db
from flaskr.utils.send_mail import send_mail


bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    return render_template('home.html')

#ログイン処理
@bp.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        pass
        
    else :
        return render_template('login.html', form=form)

#ログアウト処理
@bp.route('/logout', methods=["GET"])
def logout():
    logout_user() #ログアウト
    return redirect(url_for('app.login'))

#新規ユーザ登録処理
@bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        #名前とメールアドレス、パスワードで登録
        user = User(
            email = form.email.data, 
            password = form.password.data
        )

        user.register_user()  # ユーザーをDBに登録

        #入力されたメールアドレス宛にメールを送信する処理
        token = Auth.create_token(user.id)
        send_mail(user.email, token) #登録アドレスに認証メールを送信

        return redirect(url_for('app.login'))
    else :
        return render_template('register.html', form=form)

#新規登録後 -> 認証メール送信 -> プロフィール入力画面
@bp.route('/auth/<uuid:token>', methods=["GET", "POST"])
def auth(token):
    form = AuthForm(request.form)
    return render_template('auth.html', form=form)








