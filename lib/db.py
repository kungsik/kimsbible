import pymysql
from datetime import datetime
from flask import request

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

