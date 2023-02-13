from datetime import datetime, timedelta

from flaskr import login_manager, db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, unique=False, default=False)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now)

    #コンストラクタ
    #パスワードは暗号化する
    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    #メールアドレスから該当ユーザーを取得
    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    #IDから該当ユーザを取得
    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    #該当IDを持つユーザを有効にする(is_active=True)
    @classmethod
    def active_user_by_userid(cls, user_id):
        user = cls.query.filter_by(id=user_id).first()
        user.is_active = True
        db.session.commit()

    #ユーザーをDBに登録する
    def register_user(self):
        db.session.add(self)
        db.session.commit()

    #パスワードをチェックする
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Auth(db.Model):
    __tablename__ = 'auths'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, index=True, server_default=str(uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    #新規ユーザ登録後 -> ユーザ認証メールを送信
    @classmethod
    def create_token(cls, user_id):
        token = str(uuid4())
        new_token = cls(
            token, 
            user_id, 
            datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        db.session.commit()

        return token

    #tokenの値からユーザのidを取得する
    @classmethod
    def get_userid_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()

        if record:
            return record.user_id
        else :
            return None

class User_Info(db.Model):
    __tablename__ = 'user_infos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(64))
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(64), nullable=False)
    icon_dir = db.Column(db.Text)
    one_comment = db.Column(db.String(64))
    profile_comment = db.Column(db.Text)
    last_login = db.Column(db.DateTime, default=datetime.now)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, user_id, name, age, gender, icon_dir, one_comment, profile_comment):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.gender = gender
        self.icon_dir = icon_dir
        if one_comment == '':
            self.one_comment = 'よろしくお願いします。'
        else :
            self.one_comment = one_comment
        if profile_comment == '':
            self.profile_comment = 'よろしくお願いします'
        else :
            self.profile_comment = profile_comment

    #userIdから該当するユーザの情報を取得
    @classmethod 
    def get_name_by_userId(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    #ユーザ情報をDBに登録する
    def add_user_info(self):
        db.session.add(self)
        db.session.commit()

