from flask import Blueprint, flash
from flask import Flask, render_template, request, redirect, session
from model import User, db
from form import RegisterForm, LoginForm

blue_account = Blueprint("account", __name__, url_prefix="/account")

@blue_account.route("/register", methods=('GET', 'POST'))
def register() : 
    form = RegisterForm()
    print(form.data.get("password"), form.data.get("re_password"))
    if form.validate_on_submit() : 
        userid = form.data.get("userid")
        name = form.data.get("name")
        password = form.data.get("password")

        usertable=User(userid, name, password) #user_table 클래스
        
        db.session.add(usertable)
        db.session.commit()
        flash('회원가입을 완료하였습니다.', 'success')
        return render_template('test_login.html',form=LoginForm())

    flash('작성하신 내용을 확인해주세요.')
    return render_template('test_register.html', form=form)

@blue_account.route("/login", methods=('GET', 'POST'))
def login() : 
    message = ""
    form = LoginForm() #로그인폼
    if form.validate_on_submit(): #인증
        print('{}가 로그인 했습니다'.format(form.data.get('userid')))
        session['userid']=form.data.get('userid') #form에서 가져온 userid를 세션에 저장
        
        return redirect('/') #성공하면 main.html로
    return render_template('test_login.html', form=form, message=message)