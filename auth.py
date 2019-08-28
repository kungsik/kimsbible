from kimsbible import app
from kimsbible.lib import db
from flask import render_template, request, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

login_manager = LoginManager()
login_manager.init_app(app)

class User:
    def __init__(self, email, name, authenticated=False):
        self.user_id = email
        self.name = name
        self.authenticated = authenticated
    
    def __repr__(self):
        r = {
            'user_id': self.email,
            'name': self.name,
            'authenticated': self.authenticated
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

        user_db = db.Table()
        result = user_db.adduser(email, name, password)

        if not result:
            return redirect('/auth/signup/?existing=1')
        
        return redirect("/")

    else:
        return render_template('signup.html') 


@app.route("/auth/signin/", methods=['POST','GET'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_db = db.Table()
        result = user_db.signin_user(email, password)
       
        if not result:
            return redirect('/auth/signin/?fail=1')
        
        else: 
            passed_user = User(result[1], result[3], True)
            login_user(passed_user, remember=True)

            return render_template("signin.html", user=current_user)

    else:
        return render_template('signin.html') 

@app.route('/auth/signout/')
@login_required
def signout():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect("/")