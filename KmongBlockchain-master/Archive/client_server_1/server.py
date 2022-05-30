import os
from my_constants import app
import pyAesCrypt
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit
import socket
import pickle
from blockchain import Blockchain
import requests
import socketio
from model import User, db

# The package requests is used in the 'hash_user_file' and 'retrieve_from hash' functions to send http post requests.
# Notice that 'requests' is different than the package 'request'.
# 'request' package is used in the 'add_file' function for multiple actions.

sio = socketio.Client() 
client_ip = app.config['NODE_ADDR']
connection_status = False

blockchain = Blockchain()

# 확장자 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 파일에 확장자 추가
def append_file_extension(uploaded_file, file_path):
    file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
    user_file = open(file_path, 'a')
    user_file.write('\n' + file_extension)
    print("append_file_extension : ", user_file)
    user_file.close()

# 파일 암호화 풀기
def decrypt_file(file_path, file_key):
    encrypted_file = os.path.join(app.config['DOWNLOAD_FOLDER'], file_path[:-4].rsplit('/', 1)[-1])
    pyAesCrypt.decryptFile(file_path, encrypted_file,  file_key, app.config['BUFFER_SIZE'])

# 파일 암호화하기
def encrypt_file(file_path, file_key):
    pyAesCrypt.encryptFile(file_path, file_path + ".aes",  file_key, app.config['BUFFER_SIZE'])

# 파일 저장
def hash_user_file(user_file, file_key):
    # 파일 암호화
    encrypt_file(user_file, file_key)
    os.remove(user_file)
    encrypted_file_path = user_file + ".aes"
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files={"file":encrypted_file_path})
    response_json = response.json()
    file_hash = response_json['Hash']
    return file_hash

# 파일 다운로드
def retrieve_from_hash(file_hash, file_key):
    response = requests.post('https://ipfs.infura.io:5001/api/v0/cat?arg=' + file_hash)
    response_text = response.text.replace("\\", "/")
    print("response_text", response_text)
    # 파일 암호화 풀기
    decrypt_file(response_text, file_key)

# 파일 삭제
def delete_hash_file(file_hash, file_key) : 
    response = requests.post('https://ipfs.infura.io:5001/api/v0/cat?arg=' + file_hash)
    file_path = response.text.replace("\\", "/")
    print("Delete : file path ", file_path)
    
    # file_key 확인
    # pyAesCrypt 에는 encrypt, decrypt 메소드만 존재,
    # decrypt 메소드로 file_hash, file_key 일치 여부 확인
    encrypted_file = os.path.join(app.config['DOWNLOAD_FOLDER'], file_path[:-4].rsplit('/', 1)[-1])
    pyAesCrypt.decryptFile(file_path, encrypted_file,  file_key, app.config['BUFFER_SIZE'])
    
    if os.path.isfile(file_path) and os.path.isfile(encrypted_file) : 
        os.remove(file_path)
        os.remove(encrypted_file)
        
        print("Delete : complete remove file")
    else : print("Delete : no file")
    
# chian replace 확인
def chain_replace(): 
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')
        
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html' , message = "Welcome!")

@app.route('/download')
def download():
    return render_template('download.html' , message = "Welcome!")

@app.route('/modify')
def modify():
    return render_template('modify.html' , message = "Welcome!")

@app.route('/delete')
def delete():
    return render_template('delete.html' , message = "Welcome!")

# 파일 업로드 메소드
@app.route('/add_file', methods=['POST'])
def add_file():
    
    chain_replace()

    # 요청 메소드 확인
    if request.method == 'POST':
        error_flag = True
        
        # 파일이 없을때
        if 'file' not in request.files:
            message = 'No file part'
            
        # 파일이 있을때
        else:
            user_file = request.files['file']
            # 파일명이 빈 문자열일때
            if user_file.filename == '':
                message = 'No file selected for uploading'

            # 허용가능한 확장자인지(pdf, jpg. .등의 파일인지 확인)
            if user_file and allowed_file(user_file.filename):
                error_flag = False
                
                # 파일명이 안전한 파일이름인지 확인
                filename = secure_filename(user_file.filename)
                
                # 업로드할 파일 경로 설정
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # 파일 저장
                user_file.save(file_path)
                
                # 파일 확장자
                append_file_extension(user_file, file_path)
                
                # 블록체인에 저장할 정보들
                sender = request.form['sender_name']
                receiver = ""
                action = "create"
                file_key = request.form['file_key']
                
                try:
                    # 파일의 해시값 얻기
                    file_hash = hash_user_file(file_path, file_key)
                    # 블록체인에 블록 추가
                    blockchain.add_action(sender, receiver, action, file_hash)
                    
                except Exception as err:
                    message = str(err)
                    error_flag = True
                    if "ConnectionError:" in message:
                        message = "Gateway down or bad Internet!"
                        
            # 허용가능한 확장자가 아닐 때(pdf, jpg. .등의 파일인지 확인)
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('upload.html' , message = message)
        else:
            return render_template('upload.html' , message = "File succesfully uploaded")

# 파일 수정 메소드
@app.route('/modify_file', methods=['POST'])
def modify_file():
    
    chain_replace()

    # 요청 메소드 확인
    if request.method == 'POST':
        error_flag = True
        
        # file_hash, file_key값 받기
        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        elif request.form['file_key'] == '':
            message = 'No file key entered.'
        else:
            error_flag = False
            file_key = request.form['file_key']
            file_hash = request.form['file_hash']
            
        # 수정파일 이 없을때
        if 'file' not in request.files:
            message = 'No file part'
            
        # 수정파일이 있을때
        else:
            user_file = request.files['file']
            
            # 파일명 확인
            if user_file.filename == '':
                message = 'No file selected for uploading'

            # 파일 확장자 확인
            if user_file and allowed_file(user_file.filename):
                error_flag = False
                
                # 파일명이 안전한지 확인
                filename = secure_filename(user_file.filename)
                
                # 업로드할 파일 경로 설정
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # 파일저장
                user_file.save(file_path)
                
                # 파일 확장자
                append_file_extension(user_file, file_path)
                
                # 블록체인에 저장할 정보들
                sender = request.form['sender_name']
                receiver = ""
                action = "modify"
                file_key = request.form['file_key']
                try:
                    # 기존 파일 삭제 후
                    delete_hash_file(file_hash, file_key)
                    # 수정된 파일 추가
                    hashed_output1 = hash_user_file(file_path, file_key)
                    # 블록체인에 블록 추가
                    index = blockchain.add_action(sender, receiver, action, hashed_output1)
                    
                except Exception as err:
                    message = str(err)
                    error_flag = True
                    if "ConnectionError:" in message:
                        message = "Gateway down or bad Internet!"
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('modify.html' , message = message)
        else:
            return render_template('modify.html' , message = "File succesfully modified")

# 파일 다운로드 메소드
@app.route('/retrieve_file', methods=['POST'])
def retrieve_file():

    chain_replace()

    # 요청 메소드 확인
    if request.method == 'POST':

        error_flag = True

        # file_hash, file_key 받기
        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        elif request.form['file_key'] == '':
            message = 'No file key entered.'
        else:
            error_flag = False
            file_key = request.form['file_key']
            file_hash = request.form['file_hash']
            try:
                # 파일 다운로드
                retrieve_from_hash(file_hash, file_key)
                
                # action을 블록체인에 추가
                block = blockchain.find_block(file_hash)
                sender = block['sender']
                receiver = request.form['receiver_name']
                action = "share"
                blockchain.add_action(sender, receiver, action, file_hash)
                
            except Exception as err:
                message = str(err)
                error_flag = True
                if "ConnectionError:" in message:
                    message = "Gateway down or bad Internet!"

        if error_flag == True:
            return render_template('download.html' , message = message)
        else:
            return render_template('download.html' , message = "File successfully downloaded")

# 파일 삭제 메소드
@app.route('/delete_file', methods=['POST'])
def delete_file():

    chain_replace()

    if request.method == 'POST':

        error_flag = True

        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        elif request.form['file_key'] == '':
            message = 'No file key entered.'
        else:
            error_flag = False
            file_key = request.form['file_key']
            file_hash = request.form['file_hash']
            try:
                # 파일 삭제
                delete_hash_file(file_hash, file_key)
                

                # action을 블록체인에 추가
                print("find hash", file_hash)
                block = blockchain.find_block(file_hash)
                sender = block['sender']
                receiver = ""
                action = "delete"
                print(action)
                blockchain.add_action(sender, receiver, action, file_hash)
                
            except Exception as err:
                message = str(err)
                error_flag = True
                if "ConnectionError:" in message:
                    message = "Gateway down or bad Internet!"

        if error_flag == True:
            return render_template('delete.html' , message = message)
        else:
            return render_template('delete.html' , message = "File successfully deleted")
        
# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@sio.event
def connect():
    print('connected to server')

@sio.event
def disconnect():
    print('disconnected from server')

@sio.event
def my_response(message):
    print(pickle.loads(message['data']))
    blockchain.nodes = pickle.loads(message['data'])

@app.route('/connect_blockchain')
def connect_blockchain():
    global connection_status
    nodes = len(blockchain.nodes)
    print("nodes", nodes, connection_status)
    if connection_status is False:
        sio.connect('http://'+app.config['SERVER_IP'])
        sio.emit('add_client_node', 
                {'node_address' : client_ip['Host'] + ':' + str(client_ip['Port'])}
                )
        nodes = nodes + 1

    print("1")
    is_chain_replaced = blockchain.replace_chain()
    connection_status = True
    print("2")
    return render_template('connect_blockchain.html', messages = {'message1' : "Welcome to the services page",
                                                                  'message2' : "Congratulations , you are now connected to the blockchain.",
                                                                 } , chain = blockchain.chain, nodes = nodes)

@app.route('/disconnect_blockchain')
def disconnect_blockchain():
    global connection_status
    connection_status = False
    sio.emit('remove_client_node', 
            {'node_address' : client_ip['Host'] + ':' + str(client_ip['Port'])}
            )
    sio.disconnect()
    
    return render_template('index.html')

if __name__ == '__main__':
    
    app.run(host = client_ip['Host'], port= client_ip['Port'])