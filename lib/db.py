import pymysql
from datetime import datetime
from flask import request, redirect
from flask_login import login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

class Table:
    def __init__(self):
        self.db = pymysql.connect(
          "localhost",
          "root",
          "alphalef1351",
          "alphalef"
        )
        self.cursor = self.db.cursor()
# vcode, ip 추가해야 함
    def add(self, title, content, author, vcode):
        now = datetime.now().isoformat(' ', 'seconds')
        ip = request.remote_addr
        sql = "INSERT INTO commentary (date, title, content, author, vcode, ip) VALUES ('" + str(now) + "', '"  + title + "', '" + content + "', '" + author + "', '" + vcode + "', '" + ip +"')"
        try: 
          self.cursor.execute(sql)
          self.db.commit()
          return "insertion is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "insertion failed"
    
    def clist(self):
        sql = "SELECT * FROM commentary ORDER BY no DESC"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
    
    def cview(self, no):
        sql = "SELECT * FROM commentary WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result

    def vcode(self, no):
        sql = "SELECT * FROM commentary WHERE vcode='" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result


    # 회원 인증 관련
    def adduser(self, email, name, password):
        sql1 = "SELECT * FROM user where email='" + email + "'"
        check_user = self.cursor.execute(sql1)
        if check_user:
          return False

        sql2 = "INSERT INTO user (email, name, password) VALUES ('" + email + "', '"  + name + "', '" + generate_password_hash(password, method='sha256') + "')"
        try: 
          self.cursor.execute(sql2)
          self.db.commit()
          return "signup is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "signup failed"
    
    def signin_user(self, email, password):
        sql = "SELECT * FROM user where email='" + email + "'"
        self.cursor.execute(sql)
        user = self.cursor.fetchone()
        if not user or not check_password_hash(user[2], password):
          return False
        else:
          return user
    
    def getUserNamebyEmail(self, email):
        sql = "SELECT name FROM user where email='" + email + "'"
        self.cursor.execute(sql)
        name = self.cursor.fetchone()
        if not name:
          return False
        else:
          return name[0]
         

