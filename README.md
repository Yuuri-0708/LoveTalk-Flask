# LoveTalk-Flask

マッチング型メッセージアプリです。

使用技術
========================

| 技術             | バージョン |     
| ---------------- | ---------- | 
| Python           | 3.10.6     |     
| Flask            | 2.2.2      |     
| Flask-Login      | 0.6.2      | 
| Flask-Migrate    | 4.0.4      |  
| Flask-SQLAlchemy | 3.0.3      | 
| Jinja2           | 3.1.2      | 

ライブラリのインストール
========================

```
$ pip install -r requirements.txt
```

設定
=========================

```
$ touch .env
$ SECRET_KEY = '任意の値'　-> 下記の出力をコピー > .env

import os
os.urandom(24)
```

実行
========================

```
$ python setup.py
```

※メール認証機能(Gmail)の追加
========================

```
$ MAIL_ADDRESS = '自身のGmailアドレス' > .env
$ MAIL_PASS = '自身のGmailアプリパスワード' > .env 
```

flaskr/route.pyの70行目をコメントアウト

