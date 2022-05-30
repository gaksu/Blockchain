import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import accountAPI
from model import db
# UPLOAD_FOLDER = '/Users/souviksaha/Desktop/Blockchain-based-Decentralized-File-Sharing-System-using-IPFS/client_server_1/uploads'
# DOWNLOAD_FOLDER = '/Users/souviksaha/Desktop/Blockchain-based-Decentralized-File-Sharing-System-using-IPFS/client_server_1/downloads'

UPLOAD_FOLDER = '../uploadc'
DOWNLOAD_FOLDER = '../download'
app = Flask(__name__)

# account 기능 연동
app.register_blueprint(accountAPI.blue_account)


app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['SERVER_IP'] = '127.0.0.1:5111'
# app.config['NODE_ADDR'] = {'Host' : '127.0.0.2', 'Port' : 5113}
app.config['NODE_ADDR'] = {'Host' : '0.0.0.0', 'Port' : 5113}
app.config['BUFFER_SIZE'] = 64 * 1024
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# db 관련 변수

dbdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(dbdir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True # 사용자 요청이 끝나면 커밋=DB반영한다.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 추가 메모리 사용 끄기

db.init_app(app)
db.app = app
db.create_all()



