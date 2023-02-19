from datetime import datetime

from flask import ( 
    Blueprint, render_template, redirect, request, url_for, session, abort, 
    flash, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

from flaskr.forms import LoginForm, RegisterForm, AuthForm, EditForm, GoodForm, MessageForm
from flaskr.models import User, Auth, User_Info, MatchStatus, Message
from flaskr import db
from flaskr.utils.send_mail import send_mail
from flaskr.utils import make_message_format

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
        #send_mail(user.email, token) #登録アドレスに認証メールを送信
        print('http://127.0.0.1:5000/auth/' + token)

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
            file_name = str(user_id) + '_' + str(int(datetime.now().timestamp())) + '.jpg' #ファイル名を"(userid)_(time).jpg"とする
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
    user_info = User_Info.get_user_by_userId(user_id)
    return render_template('mypage.html', user=user, user_info=user_info)

#プロフィール編集画面
@bp.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditForm(request.form)
    user_id = current_user.get_id()
    user_info = User_Info.get_user_by_userId(user_id)
    if request.method == "POST" and form.validate():
        file = request.files[form.icon_dir.name].read() #送信されたファイル名を取得
        icon_dir = ''
        if file: #ファイルが送信されていたら、ファイルをflaskr/static/user_icon/に保存する
            file_name = str(user_id) + '_' + str(int(datetime.now().timestamp())) + '.jpg' #ファイル名を"(userid)_(time).jpg"とする
            save_path = 'flaskr/static/user_icon/' + file_name
            with open(save_path, mode='wb') as f:
                f.write(file)
            icon_dir = 'user_icon/' + file_name
        user_info.update_user_info(
            form.name.data, 
            form.age.data, 
            icon_dir, 
            form.one_comment.data, 
            form.profile_comment.data
        )
        return redirect(url_for('app.mypage'))
    return render_template('edit_profile.html', form=form, user_info=user_info)

#さがす画面
@bp.route('/user_search', methods=["GET"])
@login_required
def search_user():
    form = GoodForm()
    user_id = current_user.get_id()
    mygender = User_Info.get_user_by_userId(user_id).gender
    users = User_Info.search_user(mygender)

    return render_template('user_search.html', users=users, form=form)

#各ユーザページ
@bp.route('/users/<int:userId>', methods=["GET"])
@login_required
def user_page(userId):
    form = GoodForm()
    user = User_Info.get_user_and_good_by_userId(userId)

    return render_template('users.html', user=user, form=form)

#いいね機能
@bp.route('/good_user', methods=["POST"])
@login_required
def good_user():
    form = GoodForm(request.form)
    if request.method == "POST" and form.validate():
        if form.connect_condition.data == 'connect': #自分からのいいね
            new_good_for_me = MatchStatus(current_user.get_id(), form.to_user_id.data)
            new_good_for_me.new_good() #いいね情報をDB(match_statuses)に保存
        elif form.connect_condition.data == 'accept': #相手から先にいいねがある
            good_from_other = MatchStatus.get_good_condition_by_userId(form.to_user_id.data)
            if good_from_other:
                good_from_other.update_status() #マッチング成立

    next_url = request.referrer
    if next_url:
        return redirect(next_url)
    return redirect(url_for('app.search_user'))

#いいね履歴(自分から送信)
@bp.route('/good/sent', methods=["GET"])
@login_required
def sent_good_history():
    users = User_Info.good_history_sent()
    return render_template('good_history_sent.html', users=users)

#いいね履歴(相手から送信)
@bp.route('/good/received', methods=["GET"])
@login_required
def received_good_history():
    form = GoodForm()
    users = User_Info.good_history_received()
    return render_template('good_history_received.html', form=form, users=users)

#メッセージビュー画面(選択画面)
@bp.route('/message_view', methods=["GET"])
@login_required
def message_view():
    matched_users_info = User_Info.get_match_users()
    matched_users = MatchStatus.get_matched_user()
    matched_user_ids = []
    for matched_user in matched_users:
        if matched_user.from_user_id != int(current_user.get_id()):
            matched_user_ids.append(matched_user.from_user_id)
        elif matched_user.to_user_id != int(current_user.get_id()):
            matched_user_ids.append(matched_user.to_user_id)
        else :
            matched_user_ids.append(-1)
    last_messages = []
    for matched_user_id in matched_user_ids:
        last_messages.append(Message.get_last_message(matched_user_id, current_user.get_id()))


    return render_template('message_view.html', users = matched_users_info, message=last_messages)

#メッセージ画面
@bp.route('/message/<int:userId>', methods=["POST", "GET"])
@login_required
def message(userId):
    if not MatchStatus.is_friend(userId):
        return redirect(url_for('app.search_user'))
    form = MessageForm(request.form)
    messages = Message.get_message(int(current_user.get_id()), userId)
    user_info = User_Info.get_user_by_userId(userId)
    my_info = User_Info.get_user_by_userId(int(current_user.get_id()))

    if request.method == "POST" and form.validate():
        message = Message(
            current_user.get_id(), 
            form.to_user_id.data, 
            form.message.data
        )
        message.create_message() #メッセージをDBに保存
        return redirect(url_for('app.message', userId=userId))

    return render_template('message.html', form=form, messages=messages, user=user_info, my=my_info, to_user_id=userId)

#メッセージ更新
@bp.route('/message_ajax', methods=["GET"])
@login_required
def message_ajax():
    user_id = request.args.get('user_id', int) #メッセージの相手ID
    user_info = User_Info.get_user_by_userId(user_id)

    #まだ読んでいない相手のメッセージを取得
    not_read_messages = Message.get_not_read_message(user_id, int(current_user.get_id()))
    not_read_message_ids = [message.id for message in not_read_messages]

    #is_read = False -> Trueに変更
    if not_read_message_ids:
        Message.update_is_read(not_read_message_ids)
    
    #既に読まれたメッセージを既読にする
    not_checked_messages = Message.get_already_read_message(current_user.get_id(), user_id)
    not_checked_message_ids = [message.id for message in not_checked_messages]

    #is_checked = False -> Trueに変更
    if not_checked_message_ids:
        Message.update_is_checked(not_checked_message_ids)

    return jsonify(data = make_message_format(user=user_info, messages=not_read_messages), checked_message_ids=not_checked_message_ids)

#Page Not Found Error
@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('app.home'))

#server error
@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500        









