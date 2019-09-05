import pymysql
import re
from datetime import datetime, timedelta
from flask import request, redirect
from flask_login import login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from kimsbible.lib import vcodeparser as vp
from kimsbible.lib import config

class Table:
    def __init__(self):
        self.db = pymysql.connect(
          config.hostname,
          config.username,
          config.password,
          config.db
        )
        self.cursor = self.db.cursor()
        self.current_time = datetime.now() + timedelta(hours=9)
    
    def add_commentary(self, table, title, content, author, vcode, email):
        verse = vp.codetostr(vcode, vp.bookListKorAbbr)
        now = self.current_time.isoformat(' ')
        headers_list = request.headers.getlist("X-Forwarded-For")
        ip = headers_list[0] if headers_list else request.remote_addr

        vcode_list = vcode.split('-')
        vcode1 = vcode_list[0]
        if len(vcode_list) > 1:
          vcode2 = vcode_list[1]
        else:
          vcode2 = vcode1
        
        urltitle = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', title).replace(" ", "-")

        sql = "INSERT INTO " + table + " (date, title, content, author, vcode1, vcode2, ip, email, verse, urltitle) VALUES ('" + str(now) + "', %s, %s, '" + author + "', '" + vcode1 + "', '"  + vcode2 + "', '" + ip +"', '" + email + "', '" + verse + "', '" + urltitle + "')"
        try: 
          self.cursor.execute(sql, (title, content))
          self.db.commit()
          return "insertion is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "insertion failed"
    
    def edit_commentary(self, table, no, title, content, vcode):
        verse = vp.codetostr(vcode, vp.bookListKorAbbr)
        now = self.current_time.isoformat(' ')

        vcode_list = vcode.split('-')
        vcode1 = vcode_list[0]
        if len(vcode_list) > 1:
          vcode2 = vcode_list[1]
        else:
          vcode2 = vcode1 

        urltitle = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', title).replace(" ", "-")

        sql = "UPDATE " + table + " SET title=%s, content=%s, vcode1='" + str(vcode1) + "', vcode2='" + str(vcode2) + "', verse='" + verse + "', urltitle='" + urltitle + "', edited_date='" + now + "' WHERE no=" + str(no)
        try: 
          self.cursor.execute(sql, (title, content))
          self.db.commit()
          return "edit is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "edit failed" 
    
    def get_table_count(self, table):
        sql = "SELECT count(*) FROM " + table
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[0]

    def clist(self, table, pagenum):
        limit_end = int(pagenum) * 10
        limit_start = int(limit_end) - 9

        sql = "SELECT * FROM " + table + " ORDER BY no DESC LIMIT " + str(limit_start) + ", " + str(limit_end) 
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
    
    def cview(self, table, no):    
        # 조회수 관련 처리
        now = self.current_time.isoformat(' ')
        headers_list = request.headers.getlist("X-Forwarded-For")
        ip = headers_list[0] if headers_list else request.remote_addr

        ipcheck_sql = "SELECT no FROM ipcheck WHERE ip='" + ip + "' AND id='" + str(no) + "' AND tablename='" + table + "'"
        self.cursor.execute(ipcheck_sql)
        check_result = self.cursor.fetchone()
       
        if check_result:
          sql = "SELECT * FROM " + table + " WHERE no='" + str(no) + "'"
          self.cursor.execute(sql)
          result = self.cursor.fetchone()
        
          return result
       
        else:
          ipcheck_add_sql = "INSERT INTO ipcheck (date, ip, tablename, id) VALUES ('" + str(now) + "', '" + ip + "', '" + table + "', '" + str(no) + "')"
          self.cursor.execute(ipcheck_add_sql)
          self.db.commit()

          add_vcount_sql = "UPDATE " + table + " SET vcount=vcount+1 WHERE no='" + str(no) + "'"
          self.cursor.execute(add_vcount_sql)
          self.db.commit()

          sql = "SELECT * FROM " + table + " WHERE no='" + str(no) + "'"
          self.cursor.execute(sql)
          result = self.cursor.fetchone()
          
          return result

    def vcode_list(self, no):
        sql_commentary = "SELECT * FROM commentary WHERE vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_commentary)
        commentary_list = self.cursor.fetchall()
        
        sql_classic = "SELECT * FROM classic WHERE vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_classic)
        classic_list = self.cursor.fetchall()

        result = {}
        result['commentary'] = commentary_list
        result['classic'] = classic_list
        
        return result

    def remove_commentary(self, table, no):
        sql = "DELETE FROM " + table + " WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        self.db.commit()
        return "delete is done"

    def is_author(self, table, no, current_user):
        sql = "SELECT email FROM " + table + " WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result[0] == current_user.user_id:
          return True
        else:
          return False

    def get_recent(self, table, num):
        sql = "SELECT * FROM " + table + " ORDER BY no DESC LIMIT " + str(num)
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