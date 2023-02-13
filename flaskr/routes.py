from datetime import datetime

from flask import ( 
    Blueprint, render_template, redirect, request, url_for, session, abort, 
    flash, 
)
from flask_login import login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

from flaskr.forms import LoginForm, RegisterForm, AuthForm
from flaskr.models import User, Auth, User_Info
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
        email = form.email.data
        user = User.select_user_by_email(email)
        if not user: #該当アドレスのユーザが存在しない場合
            flash('存在しないユーザです')
            return render_template('login.html', form=form)
        elif not user.is_active == True: #ユーザが本登録を行っていない場合
            #入力されたメールアドレス宛にメールを送信する処理
            token = Auth.create_token(user.id)
            send_mail(user.email, token) #登録アドレスに認証メールを送信
            flash('本登録が完了していません。送信されたメールから本登録をしてください。')
            return render_template('login.html', form=form)
        elif not user.check_password(form.password.data):
            flash('メールアドレスとパスワードの組み合わせが間違っています')
            return render_template('login.html', form=form)

        login_user(user) #ログイン
        next = request.args.get('next')
        if not next:
            next = url_for('app.mypage')
        return redirect(next)

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

        return render_template('after_mail.html', email=user.email)
    return render_template('register.html', form=form)

#新規登録後 -> 認証メール送信 -> プロフィール入力画面
@bp.route('/auth/<uuid:token>', methods=["GET", "POST"])
def auth(token):
    form = AuthForm(request.form)
    user_id = Auth.get_userid_by_token(token)
    if not user_id:
        abort(500, 'トークンが存在しないか、有効期限が切れています')

    if request.method == "POST" and form.validate():
        file = request.files[form.icon_dir.name].read() #送信されたファイル名を取得
        icon_dir = ''
        if file: #ファイルが送信されていたら、ファイルをflaskr/static/user_icon/に保存する
            file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg' #ファイル名を"(userid)_(time).jpg"とする
            save_path = 'flaskr/static/user_icon/' + file_name
            with open(save_path, mode='wb') as f:
                f.write(file)
            icon_dir = 'user_icon/' + file_name
        user_info = User_Info(
            user_id = user_id, 
            name = form.name.data, 
            age = form.age.data, 
            gender = form.gender.data, 
            icon_dir = icon_dir,
            one_comment = form.one_comment.data, 
            profile_comment= form.profile_comment.data
        )
        user_info.add_user_info() #ユーザ情報をDBに追加
        User.active_user_by_userid(user_info.user_id) #登録処理完了後、ユーザを有効にする(users.is_active=True)

        return redirect(url_for('app.login')) #ログイン画面に遷移
    return render_template('auth.html', form=form)

#マイページ(ログイン後)
@bp.route('/mypage', methods=["GET"])
@login_required
def mypage():
    user_id = current_user.get_id()
    user = User.select_user_by_id(user_id)
    user_info = User_Info.get_name_by_userId(user_id)
    return render_template('mypage.html', user=user, user_info=user_info)

#プロフィール編集画面
@bp.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = User_Info(request.form)
    if request.method == "POST" and form.validate():
        pass
    return render_template('edit_profile.html', form=form)








