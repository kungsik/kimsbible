from kimsbible import app
from kimsbible.lib import db
from kimsbible.lib import config
from kimsbible.lib import mail
from flask import render_template, request, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from urllib import parse

login_manager = LoginManager()
login_manager.init_app(app)

def makerand():
    import string
    import random
    
    _LENGTH = 20 # 20자리
    
    # 숫자 + 대소문자 + 특수문자
    string_pool = string.ascii_letters + string.digits
    
    # 랜덤한 문자열 생성
    result = "" 
    for i in range(_LENGTH) :
        result += random.choice(string_pool) # 랜덤한 문자열 하나 선택

    return result



class User:
    def __init__(self, email, num, name, authenticated=False):
        self.user_id = email
        self.num = num
        self.name = name
        self.authenticated = authenticated
    
    def __repr__(self):
        r = {
            'user_id': self.user_id,
            'name': self.name,
            'authenticated': True
        }
        return str(r)

    def is_active(self):
        return True
    
    def get_id(self):
        return self.user_id
    
    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    user_db = db.User()
    username = user_db.getUserNamebyEmail(user_id)
    num = user_db.getUserNumbyEmail(user_id)
    return User(user_id, num, username)


@app.route("/auth/signup/", methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']
        redirecturl = parse.unquote(request.form['redirect'])

        if name == '알파알렙' or name == '관리자' or name == 'admin' or name == 'administrator' or name == '알파알렙성경':
            return render_template('signup.html', error=3, name=name, redirecturl=redirecturl)
        
        if not name or not email or not password or not password2:
            return render_template('signup.html', error=4, redirecturl=redirecturl)

        if password != password2:
            return render_template('signup.html', error=2, redirecturl=redirecturl)

        user_db = db.User()
        result = user_db.adduser(email, name, password)

        if not result:
            return render_template('signup.html', error=1)
        
        return render_template("signup_welcome.html", name=name, email=email, redirecturl=redirecturl)

    else:
        try: 
            if current_user.name:
                return redirect("/")
        except:
            return render_template('signup.html') 


@app.route("/auth/signin/", methods=['POST','GET'])
def signin():
    try:
        if current_user.name:
            return redirect("/")
    except:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            redirecturl = parse.unquote(request.form['redirect'])
            
            user_db = db.User()
            result = user_db.signin_user(email, password)
        
            if not result:
                return render_template('signin.html', error=1)
            
            else: 
                passed_user = User(result[1], result[3], True)
                login_user(passed_user, remember=True)

                return redirect(redirecturl)

        else:
            return render_template('signin.html') 


@app.route('/auth/signout/')
# @login_required
def signout():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect("/")

@app.route('/auth/findpass/', methods=['POST','GET'])
def findpass():
    if request.method == 'POST':
        email = request.form['email']
        user_db = db.User()
        user_info = user_db.getUserInfo(email)

        if not user_info:
            return render_template('sign_find_pass.html', error="입력하신 이메일은 등록되지 않았습니다")
        
        rand_str = makerand()
        user_db.add_pass_restore(email, rand_str)

        recipients = []
        recipients.append(email)
        subject = "알파알렙 성경 비밀번호 재설정"
        html = "<img src='https://app.alphalef.com/static/img/logo.png'><br><br>"
        html += "비밀번호 변경 링크 안내<br><br>"
        html += "안녕하세요? 본 메일은 알파알렙 성경을 통해 발송된 메일입니다.<br>"
        html += "본 메일은 비밀번호 찾기를 신청하셔서 발송되었습니다. 아래 링크를 클릭하시면 회원정보와 비밀번호를 변경하실 수 있습니다.<br>"
        html += "<a href='https://app.alphalef.com/auth/info/?randstr=" + rand_str + "'>비밀번호 변경</a><br><br>"
        html += "위 링크는 당일 자정까지 유효합니다. 비밀번호 찾기를 신청하지 않으셨다면 이 메일을 무시하셔도 좋습니다."

        mail.sendmail(recipients, subject, html)

        return render_template('sign_find_pass.html', error="비밀번호 재설정 링크가 정상적으로 발송되었습니다.")
    
    else:
        return render_template('sign_find_pass.html')


@app.route('/auth/remove/', methods=['POST','GET'])
def removeuser():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        if current_user.user_id == email:

            user_db = db.User() 
            user_info = user_db.signin_user(email, password)

            if user_info:
                user_db.removeUser(email)

                current_user.authenticated = False
                logout_user()

                return render_template('sign_remove_user.html', msg="정상적으로 탈퇴 처리되었습니다.")
            
            else:
                return render_template('sign_remove_user.html', msg="잘못된 비밀번호를 입력하셨습니다.")    
        
        else:
            return render_template('sign_remove_user.html', msg="잘못된 이메일을 입력하셨습니다.")
    
    else:
        return render_template('sign_remove_user.html')



@app.route('/auth/info/', methods=['POST','GET'])
def show_member_info():
    if request.method == 'POST':

        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']
        open_email = request.form['open_email']
        randstr = request.form['randstr']

        user_db = db.User()
        if not randstr:
            user_info = user_db.getUserInfo(current_user.user_id)

        # 이메일 링크를 통해 회원 정보를 수정하려는 경우
        else:
            try:
                email = user_db.getEmailbyRand(randstr)
                user_info = user_db.getUserInfo(email)
            except:
                return redirect("/")
            
       
        if name == '알파알렙' or name == '관리자' or name == 'admin' or name == 'administrator' or name == '알파알렙성경':
            return render_template('user_info.html', error=3, user_info=user_info, name=name)
        
        if not name or not email:
            return render_template('user_info.html', error=4, user_info=user_info)

        if password != password2:
            return render_template('user_info.html', error=2, user_info=user_info)

        if not randstr:
            email = current_user.user_id
        
        result = user_db.edituser(email, name, password, open_email)

        if randstr:
            user_db.removeRand(randstr)

        if not result:
            return render_template('user_info.html', error=1, user_info=user_info)
        
        user_info = user_db.getUserInfo(email)
        return render_template('user_info.html', user_info=user_info)
    

    elif request.args.get('randstr') and request.method == 'GET':
        randstr = request.args.get('randstr')
        user_db = db.User()
        email = user_db.getEmailbyRand(randstr)
        user_info = user_db.getUserInfo(email)
        return render_template('user_info.html', user_info=user_info, randstr=randstr)


    else:
        try:
            user_db = db.User()
            user_info = user_db.getUserInfo(current_user.user_id)
            return render_template('user_info.html', user_info=user_info)

        except:
            return redirect('/')