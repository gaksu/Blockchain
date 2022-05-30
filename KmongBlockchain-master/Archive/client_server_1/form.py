from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import check_password_hash

from model import User

class RegisterForm(FlaskForm):
    
    userid = StringField('userid', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()]) #비밀번호 확인
    re_password = PasswordField('re_password', validators=[EqualTo('password')])
    
class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
            
        def __call__(self, form, field):
            userid = form['userid'].data
            password = field.data
            
            usertable = User.query.filter_by(userid=userid).first()
            if usertable : 
                if not usertable.check_password(password) : 
                    raise ValueError("비밀번호 틀림")
            else : 
                raise ValueError("아이디 없음")
                
                
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()])