from datetime import datetime, timedelta

from flaskr import login_manager, db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from uuid import uuid4

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
    
    #ユーザーをDBに登録する
    def register_user(self):
        db.session.add(self)
        db.session.commit()

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
