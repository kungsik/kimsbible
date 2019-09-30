import pymysql
import re
from datetime import datetime, timedelta
from flask import request, redirect
from flask_login import login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from kimsbible.lib import vcodeparser as vp
from kimsbible.lib import config

class Commentary:
    def __init__(self):
        self.db = pymysql.connect(
          config.hostname,
          config.username,
          config.password,
          config.db
        )
        self.cursor = self.db.cursor()
        self.current_time = datetime.now() + timedelta(hours=9)
    
    def add_commentary(self, table, title, content, author, vcode, email, copen):
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

        sql = "INSERT INTO " + table + " (date, title, content, author, vcode1, vcode2, ip, email, verse, urltitle, copen) VALUES ('" + str(now) + "', %s, %s, '" + author + "', '" + vcode1 + "', '"  + vcode2 + "', '" + ip +"', '" + email + "', '" + verse + "', '" + urltitle + "', '" + str(copen) + "')"
        try: 
          self.cursor.execute(sql, (title, content))
          self.db.commit()
          return "insertion is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "insertion failed"
    
    def edit_commentary(self, table, no, title, content, vcode, copen):
        verse = vp.codetostr(vcode, vp.bookListKorAbbr)
        now = self.current_time.isoformat(' ')

        vcode_list = vcode.split('-')
        vcode1 = vcode_list[0]
        if len(vcode_list) > 1:
          vcode2 = vcode_list[1]
        else:
          vcode2 = vcode1 

        urltitle = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', title).replace(" ", "-")

        sql = "UPDATE " + table + " SET title=%s, content=%s, vcode1='" + str(vcode1) + "', vcode2='" + str(vcode2) + "', verse='" + verse + "', urltitle='" + urltitle + "', edited_date='" + now + "', copen='" + str(copen) + "' WHERE no=" + str(no)
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
        limit_start = int(limit_end) - 10

        sql = "SELECT * FROM " + table + " WHERE copen='1' ORDER BY no DESC LIMIT " + str(limit_start) + ", 10"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def myclist(self, table, pagenum, user_id):
        limit_end = int(pagenum) * 10
        limit_start = int(limit_end) - 10

        sql = "SELECT * FROM " + table + " WHERE email='" + user_id + "' ORDER BY no DESC LIMIT " + str(limit_start) + ", 10"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
    
    def cview(self, table, no):    
        # 비공개 글일 경우 조회수 업데이트 안 함.
        copen_check_sql = "SELECT copen FROM " + table + " WHERE no='" + str(no) + "'"
        self.cursor.execute(copen_check_sql)
        is_copen = self.cursor.fetchone()

        # 조회수 관련 처리
        now = self.current_time.isoformat(' ')
        headers_list = request.headers.getlist("X-Forwarded-For")
        ip = headers_list[0] if headers_list else request.remote_addr

        ipcheck_sql = "SELECT no FROM ipcheck WHERE ip='" + ip + "' AND id='" + str(no) + "' AND tablename='" + table + "'"
        self.cursor.execute(ipcheck_sql)
        check_result = self.cursor.fetchone()
       
        if check_result or is_copen[0] == 0:
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
        sql_commentary = "SELECT * FROM commentary WHERE copen='1' and vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_commentary)
        commentary_list = self.cursor.fetchall()
        
        sql_classic = "SELECT * FROM classic WHERE copen='1' and vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_classic)
        classic_list = self.cursor.fetchall()

        result = {}
        result['commentary'] = commentary_list
        result['classic'] = classic_list
        
        return result
  
    def vcode_mylist(self, no, user_id):
        sql_my_commentary = "SELECT * FROM commentary WHERE email='" + user_id + "' and vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_my_commentary)
        commentary_my_list = self.cursor.fetchall()

        mylist = list(commentary_my_list)

        sql_other_commentary = "SELECT * FROM commentary WHERE email NOT IN ('" + user_id + "') and copen='1' and vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_other_commentary)
        commentary_other_list = self.cursor.fetchall()

        otherlist = list(commentary_other_list)

        sql_classic = "SELECT * FROM classic WHERE vcode1 <= '" + str(no) + "' and vcode2 >= '" + str(no) + "' ORDER BY no DESC"
        self.cursor.execute(sql_classic)
        classic_list = self.cursor.fetchall()

        result = {}
        commentary = mylist + otherlist

        result['commentary'] = commentary
        result['classic'] = classic_list

        return result

    def remove_commentary(self, table, no):
        sql = "DELETE FROM " + table + " WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        self.db.commit()
        return "delete is done"

    def get_recent(self, table, num):
        sql = "SELECT * FROM " + table + " WHERE copen='1' ORDER BY no DESC LIMIT " + str(num)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

class User:
    def __init__(self):
        self.db = pymysql.connect(
          config.hostname,
          config.username,
          config.password,
          config.db
        )
        self.cursor = self.db.cursor()
        self.current_time = datetime.now() + timedelta(hours=9)

    # 회원 인증 관련
    def adduser(self, email, name, password):
        sql1 = "SELECT * FROM user where email='" + email + "'"
        check_user = self.cursor.execute(sql1)
        if check_user:
          return False

        sql2 = "INSERT INTO user (email, name, password, open_email) VALUES ('" + email + "', '"  + name + "', '" + generate_password_hash(password, method='sha256') + "', '0')"
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

    def getUserNumbyEmail(self, email):
        sql = "SELECT no FROM user where email='" + email + "'"
        self.cursor.execute(sql)
        num = self.cursor.fetchone()
        if not num:
          return False
        else:
          return num[0]
    
    def getUserInfo(self, email):
        sql = "SELECT * FROM user WHERE email='" + email + "'"
        self.cursor.execute(sql)
        info = self.cursor.fetchone()
        if not info:
          return False
        else:
          return info
    
    def edituser(self, email, name, password, open_email):
       
        if password:
          pass_query = "', password='" + generate_password_hash(password, method='sha256')
        else:
          pass_query = ''

        sql2 = "UPDATE user SET email='" + email + "', name='"  + name + pass_query +  "', open_email='"  + open_email + "' WHERE email='" + email +"'"
        print(sql2)
        try: 
          self.cursor.execute(sql2)
          self.db.commit()
          return "edit is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "edit failed"
    
    def is_author(self, table, no, current_user):
        sql = "SELECT email FROM " + table + " WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result[0] == current_user.user_id:
          return True
        else:
          return False
    
    def is_open_email(self, email):
        sql = "SELECT open_email FROM user WHERE email='" + email  + "'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result[0] == 1:
          return True
        else:
          return False

    def get_identity(self, email):
        try:
          email_open = self.is_open_email(email)
          if email_open:
            return email
          else:
            return '#' + str(self.getUserNumbyEmail(email))

        except:
          return "탈퇴함"        
    
    def add_pass_restore(self, email, randstr):
        sql = "INSERT INTO restorepass (randstr, email) VALUES ('" + randstr + "', '" + email + "')"
        self.cursor.execute(sql)
        self.db.commit()
        return "insert is done"
    
    def getEmailbyRand(self, randstr):
        sql = "SELECT email FROM restorepass WHERE randstr='" + randstr + "'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[0]
    
    def removeRand(self, randstr):
        sql = "DELETE FROM restorepass WHERE randstr='" + randstr + "'"
        self.cursor.execute(sql)
        self.db.commit()
        return "delete is done"
    
    def removeUser(self, email):
        sql = "DELETE FROM user WHERE email='" + email + "'"
        self.cursor.execute(sql)
        self.db.commit()
        return "delete is done"

        


class Forum:
    def __init__(self):
        self.db = pymysql.connect(
          config.hostname,
          config.username,
          config.password,
          config.db
        )
        self.cursor = self.db.cursor()
        self.current_time = datetime.now() + timedelta(hours=9)
    
    def add_topic(self, topic, content, author, email):
        now = self.current_time.isoformat(' ')
        headers_list = request.headers.getlist("X-Forwarded-For")
        ip = headers_list[0] if headers_list else request.remote_addr

        # 새로운 토픽의 카테고리는 1로 설정함. 
        sql = "INSERT INTO forum (date, topic, content, author, ip, email, updated_date, category) VALUES ('" + str(now) + "', %s, %s, '" + author + "', '" + ip +"', '" + email + "', '" + now + "', '1')"
        try: 
          self.cursor.execute(sql, (topic, content))
          self.db.commit()
          return "insertion is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "insertion failed"
    
    def list_topic(self):
        sql = "SELECT * FROM forum WHERE category='1' ORDER BY updated_date DESC"
        try:
          self.cursor.execute(sql)
          forum_list = self.cursor.fetchall()
          return forum_list
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "load db failed" 

    def get_recent_topic(self, num):
        sql = "SELECT * FROM forum WHERE category='1' ORDER BY date DESC LIMIT " + str(num)
        try:
          self.cursor.execute(sql)
          recent_forum_list = self.cursor.fetchall()
          return recent_forum_list
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "load db failed" 
    
    def view_topic(self, no):
        sql = "SELECT * FROM forum WHERE no=" + str(no)
        try:
          self.cursor.execute(sql)
          view = self.cursor.fetchone()
          return view
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "load db failed" 

    def add_reply(self, topic_no, content, author, email):
        now = self.current_time.isoformat(' ')
        headers_list = request.headers.getlist("X-Forwarded-For")
        ip = headers_list[0] if headers_list else request.remote_addr

        # 토픽의 답변 카테고리는 2로 설정함. 
        sql = "INSERT INTO forum (date, topic_no, content, author, ip, email, category) VALUES ('" + str(now) + "', '" + str(topic_no) + "',  %s, '" + author + "', '" + ip +"', '" + email + "', '2')"

        # 토픽의 updated_date를 새롭게 갱신
        sql2 = "UPDATE forum SET updated_date='" + now + "', threads=threads+1 WHERE no='" + str(topic_no) + "'"

        try: 
          self.cursor.execute(sql, (content))
          self.db.commit()
          self.cursor.execute(sql2)
          self.db.commit()
          return "insertion is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "insertion failed"
    
    def view_reply(self, no):
        sql = "SELECT * FROM forum WHERE topic_no='" + str(no) + "' AND category='2' ORDER BY no ASC"
        self.cursor.execute(sql)
        reply_list = self.cursor.fetchall()
        return reply_list

    def edit(self, no, topic, content):
        now = self.current_time.isoformat(' ')
        sql = "UPDATE forum SET edited_date='" + now + "', content='" + content + "', topic='" + topic + "' WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        self.db.commit()
        return "successfully edited"

    def get_topicid(self, no):
        sql = "SELECT topic_no FROM forum WHERE no='" + str(no) + "' AND category='2'"
        self.cursor.execute(sql)
        topicid = self.cursor.fetchone()
        if topicid:
          return topicid[0]
        else:
          return False
    
    def remove_topic(self, no):
        if self.get_topicid(no):            
          sql2 = "UPDATE forum SET threads=threads-1 WHERE no='" + str(self.get_topicid(no)) + "'"
          self.cursor.execute(sql2)
          self.db.commit()        

        sql = "DELETE FROM forum WHERE no='" + str(no) + "'"
        self.cursor.execute(sql)
        self.db.commit()

        return "delete is done"


class Page:
    def __init__(self):
        self.db = pymysql.connect(
          config.hostname,
          config.username,
          config.password,
          config.db
        )
        self.cursor = self.db.cursor()
    
    def add_page(self, title, content, pageurl):
        sql = "INSERT INTO page (title, content, url) VALUES (%s, %s, %s)"
        try: 
          self.cursor.execute(sql, (title, content, pageurl))
          self.db.commit()
          return "insertion is done"
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "insertion failed"
    
    def view_page(self, pageurl):
        sql = "SELECT * FROM page WHERE url='" + str(pageurl) + "'"
        print(sql)
        try:
          self.cursor.execute(sql)
          view = self.cursor.fetchone()
          return view
        except pymysql.InternalError as error:
          code, message = error.args
          print(">>>>>>>>>>>>>", code, message)
          return "load db failed" 

    def edit_page(self, title, content, pageurl):
        sql = "UPDATE page SET title='" + title + "', content='" + content + "', url='" + pageurl + "' WHERE url='" + pageurl + "'"
        self.cursor.execute(sql)
        self.db.commit()
        return "successfully edited"