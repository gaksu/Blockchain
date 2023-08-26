import os
import urllib.request
import ipfshttpclient
from my_constants import app
import pyAesCrypt
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit
import socket
import pickle
from blockchain import Blockchain
from UserDAO import UserDAO
import requests
import socketio
from sqlalchemy import create_engine
import shutil
# The package requests is used in the 'hash_user_file' and 'retrieve_from hash' functions to send http post requests.
# Notice that 'requests' is different than the package 'request'.
# 'request' package is used in the 'add_file' function for multiple actions.

sio = socketio.Client() 
client_ip = app.config['NODE_ADDR']
connection_status = False

blockchain = Blockchain()
userDao = UserDAO()

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
    print("decrypt_file file path", file_path)
    print("ee",encrypted_file)
    # os.rename(file_path, encrypted_file)
    pyAesCrypt.decryptFile(file_path, encrypted_file,  file_key, app.config['BUFFER_SIZE'])

# 파일 암호화하기
def encrypt_file(file_path, file_key):
    pyAesCrypt.encryptFile(file_path, file_path + ".aes",  file_key, app.config['BUFFER_SIZE'])

# 파일 해쉬값 얻기
def hash_user_file(user_file, file_key):
    encrypt_file(user_file, file_key)
    os.remove(user_file)
    encrypted_file_path = user_file + ".aes"
    print("hash_user_file")
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files={"file":encrypted_file_path})
    print("1")
    # response = client.add(encrypted_file_path)
    print("1", response)
    response_json = response.json()
    file_hash = response_json['Hash']
    return file_hash

# 해쉬값으로 파일 경로
def retrieve_from_hash(file_hash, file_key):
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    response = requests.post('https://ipfs.infura.io:5001/api/v0/cat?arg=' + file_hash)
    print("retrieve_from_hash")
    print("response.text", response.text)
    response_text = response.text.replace("\\", "/")
    print("response_text", response_text)
    # file_content = client.cat(file_hash)
    file_name = response_text.rsplit('/', 1)[-1].rsplit('.', 1)

    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_hash)
    # user_file = open(file_path, 'ab+')
    # user_file = open(file_path, 'w')
    # user_file.write(file_content)
    # user_file.close()
    
    # file = decrypt_file(response_text, file_key)
    decrypt_file(response_text, file_key)
    # with open(file_path, 'rb') as f:
    #     lines = f.read().splitlines()
    #     last_line = lines[-1]
    # user_file.close()
    # file_extension = last_line
    # saved_file = file_path + '.' + file_extension.decode()
    # os.rename(file_path, saved_file)
    # print(saved_file)
    # return saved_file

def delete_hash_file(file_hash, file_key) : 
    # 파일 삭제
    response = requests.post('https://ipfs.infura.io:5001/api/v0/cat?arg=' + file_hash)
    file_path = response.text.replace("\\", "/")
    print("Delete : file path ", file_path)
    if os.path.isfile(file_path) : 
        os.remove(file_path)
        print("Delete : complete remove file")
    else : print("Delete : no file")

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

@app.route('/add_file', methods=['POST'])
def add_file():
    
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')

    if request.method == 'POST':
        error_flag = True
        if 'file' not in request.files:
            message = 'No file part'
        else:
            user_file = request.files['file']
            if user_file.filename == '':
                message = 'No file selected for uploading'

            if user_file and allowed_file(user_file.filename):
                error_flag = False
                filename = secure_filename(user_file.filename)
                # filename = user_file.filename
                # print("filename", filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # print("file_path", file_path)
                user_file.save(file_path)
                append_file_extension(user_file, file_path)
                sender = request.form['sender_name']
                receiver = request.form['receiver_name']
                action = "create"
                file_key = request.form['file_key']
                try:
                    hashed_output1 = hash_user_file(file_path, file_key)
                    # 블록체인에 블록 추가
                    index = blockchain.add_action(sender, receiver, action, hashed_output1)
                except Exception as err:
                    message = str(err)
                    error_flag = True
                    if "ConnectionError:" in message:
                        message = "Gateway down or bad Internet!"
                # message = f'File successfully uploaded'
                # message2 =  f'It will be added to Block {index-1}'
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('upload.html' , message = message)
        else:
            return render_template('upload.html' , message = "File succesfully uploaded")

@app.route('/modify_file', methods=['POST'])
def modify_file():
    
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')

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
            
        # 수정할 파일 받기
        if 'file' not in request.files:
            message = 'No file part'
        else:
            user_file = request.files['file']
            if user_file.filename == '':
                message = 'No file selected for uploading'

            if user_file and allowed_file(user_file.filename):
                error_flag = False
                filename = secure_filename(user_file.filename)
                # filename = user_file.filename
                print("filename", filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print("file_path", file_path)
                user_file.save(file_path)
                append_file_extension(user_file, file_path)
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
                # message = f'File successfully uploaded'
                # message2 =  f'It will be added to Block {index-1}'
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('upload.html' , message = message)
        else:
            return render_template('upload.html' , message = "File succesfully uploaded")

@app.route('/retrieve_file', methods=['POST'])
def retrieve_file():

    is_chain_replaced = blockchain.replace_chain()

    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')

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
                # 파일 다운로드
                retrieve_from_hash(file_hash, file_key)
                
                # action을 블록체인에 추가
                print("find hash", file_hash)
                block = blockchain.find_block(file_hash)
                sender = block['sender']
                receiver = block['receiver']
                action = "share"
                print(action)
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


@app.route('/delete_file', methods=['POST'])
def delete_file():

    is_chain_replaced = blockchain.replace_chain()

    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')

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
            return render_template('download.html' , message = message)
        else:
            return render_template('download.html' , message = "File successfully downloaded")
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