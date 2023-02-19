from datetime import datetime, timedelta

from flaskr import login_manager, db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, desc

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
    is_active = db.Column(db.Boolean, unique=False, default=False)
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
    def get_user_by_userId(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    #userIdから該当ユーザの情報(いいね情報を付与)を取得
    @classmethod 
    def get_user_and_good_by_userId(cls, user_id):
        match_status1 = aliased(MatchStatus) #from_user_id: 相手のID, to_user_id: ログインユーザのID
        match_status2 = aliased(MatchStatus) #to_user_id: 相手のID, from_user_id: ログインユーザのID

        return cls.query.filter_by(
            user_id = user_id
        ).outerjoin(
            match_status1, 
            and_(
                match_status1.from_user_id == user_id,
                match_status1.to_user_id == current_user.get_id()
            )
        ).outerjoin(
            match_status2, 
            and_(
                match_status2.from_user_id == current_user.get_id(), 
                match_status2.to_user_id == user_id
            )
        ).with_entities(
            cls.user_id, cls.name, cls.age, cls.icon_dir,
            cls.one_comment, cls.profile_comment,
            match_status1.status.label('from_other'), 
            match_status2.status.label('from_me')
        ).first()

    #さがす画面(絞り込みなし)
    @classmethod 
    def search_user(cls, mygender):
        match_status1 = aliased(MatchStatus) #from_user_id: 相手のID, to_user_id: ログインユーザのID
        match_status2 = aliased(MatchStatus) #to_user_id: 相手のID, from_user_id: ログインユーザのID

        return cls.query.filter(
            cls.user_id != int(current_user.get_id()), 
            cls.gender != mygender, 
            cls.is_active == True
        ).outerjoin(
            match_status1, 
            and_(
                match_status1.from_user_id == cls.user_id, 
                match_status1.to_user_id == current_user.get_id()
            )
        ).outerjoin(
            match_status2, 
            and_(
                match_status2.from_user_id == current_user.get_id(), 
                match_status2.to_user_id == cls.id
            )
        ).with_entities(
            cls.user_id, cls.name, cls.age, cls.icon_dir,
            cls.one_comment,  
            match_status1.status.label('from_other'), 
            match_status2.status.label('from_me')
        ).all()

    #いいね履歴(自分から)
    @classmethod
    def good_history_sent(cls):
        match_status = aliased(MatchStatus) #from_user_id: 自分のID、to_user_id: 相手のID

        return cls.query.filter(
            cls.user_id != current_user.get_id(), 
            cls.is_active == True
        ).join(
            match_status, 
            and_(
                match_status.from_user_id == current_user.get_id(), 
                match_status.to_user_id == cls.id
            )
        ).with_entities(
            cls.user_id, cls.name, cls.age, cls.icon_dir, 
            cls.one_comment, 
            match_status.status.label('from_me')
        ).all()

    #いいね履歴(相手から)
    @classmethod
    def good_history_received(cls):
        match_status = aliased(MatchStatus) #to_user_id: 自分のID、from_user_id: 相手のID

        return cls.query.filter(
            cls.user_id != current_user.get_id(), 
            cls.is_active == True
        ).join(
            match_status, 
            and_(
                match_status.to_user_id == current_user.get_id(), 
                match_status.from_user_id == cls.id
            )
        ).with_entities(
            cls.user_id, cls.name, cls.age, cls.icon_dir, 
            cls.one_comment, 
            match_status.status.label('from_other')
        ).all()
    
    #メッセージビュー画面(マッチングした異性を取得)
    @classmethod
    def get_match_users(cls):

        return cls.query.filter(
            cls.user_id != current_user.get_id(), 
            cls.is_active == True
        ).join(
            MatchStatus, 
            or_( 
                and_( #自分からのいいねでマッチング
                    MatchStatus.from_user_id == current_user.get_id(), 
                    MatchStatus.to_user_id == cls.id, 
                    MatchStatus.status == 2
                ), 
                and_( #相手からのいいねでマッチング
                    MatchStatus.from_user_id == cls.id, 
                    MatchStatus.to_user_id == current_user.get_id(), 
                    MatchStatus.status == 2
                )
            )
        ).with_entities(
            cls.user_id ,cls.name, cls.age, cls.icon_dir
        ).all()


    #ユーザ情報をDBに登録する
    def add_user_info(self):
        self.is_active = True
        db.session.add(self)
        db.session.commit()

    #ユーザ情報を更新
    def update_user_info(self, name, age, icon_dir, one_comment, profile_comment):
        self.name = name
        self.age = age
        self.icon_dir = icon_dir
        self.one_comment = one_comment
        self.profile_comment = profile_comment
        self.updatedAt = datetime.now()

        db.session.commit()

#ユーザー同士のマッチング状態を管理
class MatchStatus(db.Model):

    __tablename__ = 'match_statuses'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) #どのユーザからのいいねか
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) #どのユーザへのいいねか
    status = db.Column(db.Integer, unique=False, default=1) #1: いいね申請中, 2: いいね承認(マッチ)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now)

    #コンストラクタ
    def __init__(self, from_user_id, to_user_id):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id

    #いいね送信(from -> どのユーザからのいいねか、to -> どのユーザへのいいねか)
    def new_good(self):
        db.session.add(self)
        db.session.commit()

    #マッチング成立(status = 1 -> 2)
    def update_status(self):
        self.status = 2
        self.updatedAt = datetime.now()
        db.session.commit()

    #ユーザーIDから自身へのいいねの状態を取得(いいねされていない場合はNone)
    @classmethod
    def get_good_condition_by_userId(cls, user_id):
        record = cls.query.filter_by(
            from_user_id = user_id, 
            to_user_id = current_user.get_id()
        ).first()

        if not record:
            return None
        return record

    #マッチングしているか
    @classmethod 
    def is_friend(cls, user_id):
        user = cls.query.filter(
            or_(
                and_(
                    cls.from_user_id == current_user.get_id(), 
                    cls.to_user_id == user_id,
                    cls.status == 2
                ), 
                and_(
                    cls.from_user_id == user_id, 
                    cls.to_user_id == current_user.get_id(), 
                    cls.status == 2
                )
            )
        ).first()

        return True if user else False

    #自分とマッチングしている人を取得
    @classmethod 
    def get_matched_user(cls):
        return cls.query.filter(
            or_(
                and_(
                    cls.from_user_id == current_user.get_id(), 
                    cls.status == 2
                ), 
                and_(
                    cls.to_user_id == current_user.get_id(), 
                    cls.status == 2
                )
            )
        ).order_by(cls.id).all()

#ユーザのメッセージを管理
class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) #どのユーザからのメールか
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) #どのユーザへのメールか
    is_read = db.Column(db.Boolean, default=False)
    is_checked = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now)

    #コンストラクタ
    def __init__(self, from_user_id, to_user_id, message):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message = message

    #新しいメッセージを追加
    def create_message(self):
        db.session.add(self)
        db.session.commit()

    #マッチング相手とのメッセージを取得
    @classmethod
    def get_message(cls, id1, id2):
        return cls.query.filter(
            or_(
                and_(
                    cls.from_user_id == id1, 
                    cls.to_user_id == id2
                ), 
                and_(
                    cls.from_user_id == id2, 
                    cls.to_user_id == id1
                )
            )
        ).order_by(desc(cls.id)).all()

    #まだ読んでいない相手のメッセージを取得(isread = False)
    @classmethod
    def get_not_read_message(cls, from_user_id, to_user_id):
        return cls.query.filter(
            cls.from_user_id == from_user_id, 
            cls.to_user_id == to_user_id, 
            cls.is_read == False
        ).order_by(cls.id).all()

    #既に読んだメッセージを既読にする(isread -> True)
    @classmethod
    def update_is_read(cls, ids):
        cls.query.filter(cls.id.in_(ids)).update(
            {'is_read': 1}, 
            synchronize_session='fetch'
        )
        db.session.commit()

    #既に読まれた自分のメッセージを取得する(is_read = True & is_checked = False)
    @classmethod
    def get_already_read_message(cls, from_user_id, to_user_id):
        return cls.query.filter(
            cls.from_user_id == from_user_id, 
            cls.to_user_id == to_user_id, 
            cls.is_read == True, 
            cls.is_checked == False
        ).order_by(cls.id).all()
    
    #既に読まれたメッセージを既読にする(is_checked -> True)
    @classmethod
    def update_is_checked(cls, ids):
        cls.query.filter(cls.id.in_(ids)).update(
            {'is_checked': 1}, 
            synchronize_session='fetch'
        )
        db.session.commit()

    #最後のメッセージを取得()
    @classmethod 
    def get_last_message(cls, id1, id2):
        return cls.query.filter(
            or_(
                and_(
                    cls.from_user_id == id1, 
                    cls.to_user_id == id2
                ), 
                and_(
                    cls.from_user_id == id2, 
                    cls.to_user_id == id1
                )
            )
        ).order_by(desc(cls.id)).first()







