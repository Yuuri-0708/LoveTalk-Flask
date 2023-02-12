import os
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

#SMTP認証
my_account = os.environ.get("MAIL_ADDRESS")
my_password = os.environ.get("MAIL_PASS")

my_email = 'lovetalkapp777@gmail.com'

#ユーザのメールアドレス宛にメールを送信
def send_mail(email, token):
    to_email = email #送信先
    from_email = my_email #送信元

    #MIMEの作成
    subject = "認証メール"
    message = f"""
        <p>まだ登録が完了していません。</p>
        <p>下記のURLにアクセスして登録を完了させてください。</p>

        <a href=http://127.0.0.1:5000/auth/{token}>登録完了はこちらから</a>
    """

    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['To'] = to_email
    msg['From'] = from_email

    print(msg['To'] + ' 認証メールを送信しました')

    #メール送信
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(my_account, my_password)
    server.send_message(msg)
    server.quit()
