from kimsbible import app
from kimsbible.lib import db
from flask import render_template, request, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from urllib import parse

login_manager = LoginManager()
login_manager.init_app(app)

class User:
    def __init__(self, email, name, authenticated=False):
        self.user_id = email
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
    user_db = db.Table()
    username = user_db.getUserNamebyEmail(user_id)
    return User(user_id, username)


@app.route("/auth/signup/", methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']
        redirecturl = parse.unquote(request.form['redirect'])

        print(redirecturl)

        if name == '알파알렙' or name == '관리자' or name == 'admin' or name == 'administrator' or name == '알파알렙성경':
            return render_template('signup.html', error=3, name=name, redirecturl=redirecturl)
        
        if not name or not email or not password or not password2:
            return render_template('signup.html', error=4, redirecturl=redirecturl)

        if password != password2:
            return render_template('signup.html', error=2, redirecturl=redirecturl)

        user_db = db.Table()
        result = user_db.adduser(email, name, password)

        if not result:
            return render_template('signup.html', error=1)
        
        return render_template("signup_welcome.html", name=name, email=email, redirecturl=redirecturl)

    else:
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
            
            user_db = db.Table()
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
@login_required
def signout():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect("/")