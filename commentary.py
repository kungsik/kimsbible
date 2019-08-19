from flask import render_template, request, url_for, redirect
from kimsbible import app
from kimsbible.lib import db
from kimsbible import oauth
import json

@app.route('/commentary/add/', methods=['POST','GET'])
def commentary_add():
    if request.method == 'POST':
        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']
        commentary_author = oauth.getAuthorizedName()

        commentary_db = db.Table()
        commentary_db.add(commentary_title, commentary_text, commentary_author, commentary_vcode)
        
        return redirect("/commentary/list/")

    else:
        return render_template('commentary_add.html')

@app.route('/commentary/list/')
def commentary_list():
    name = oauth.getAuthorizedName()
    commentary_db = db.Table()
    clist = commentary_db.clist()
    return render_template('commentary_list.html', lists=clist, name=name)

@app.route('/commentary/view/<int:no>')
def commentary_view(no):
    commentary_db = db.Table()
    cview = commentary_db.cview(no)
    return render_template('commentary_view.html', view=cview)
