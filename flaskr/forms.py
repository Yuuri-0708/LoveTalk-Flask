from wtforms.fields import (
     StringField, FileField, IntegerField, PasswordField, TextAreaField, HiddenField, SubmitField, 
     IntegerRangeField, SelectField
)
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Email, NumberRange
from wtforms import ValidationError
from flaskr.models import User, Auth


class LoginForm(FlaskForm):
    email = StringField('メールアドレス : ', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード : ', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegisterForm(FlaskForm):
    email = StringField('メールアドレス : ', validators=[DataRequired(), Email('正しいメールアドレスを入力してください')])
    password = PasswordField('パスワード : ', validators=[DataRequired(), EqualTo('confirm', 'パスワードが一致しません')])
    confirm = PasswordField('パスワード(確認用) : ', validators=[DataRequired()])
    submit = SubmitField('登録する')

    #もし、メールアドレスが既に登録されていたらerror
    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスが既に登録されています')

class AuthForm(FlaskForm):
    user_id = HiddenField()
    name = StringField('ニックネーム : ', validators=[DataRequired()])
    age = IntegerField('年齢 : ', validators=[DataRequired()])
    gender = SelectField('性別(後で変更することはできません) : ', choices=['男性', '女性'], validators=[DataRequired()])
    icon_dir = FileField('アイコン画像 : ')
    one_comment = StringField('一言コメント : ')
    profile_comment = TextAreaField('プロフィール文章 : ')
    submit = SubmitField('入力内容を送信する')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False

        return True


