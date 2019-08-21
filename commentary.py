from flask import render_template, request, url_for, redirect, session
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
        commentary_author = session['username']

        commentary_db = db.Table()
        commentary_db.add(commentary_title, commentary_text, commentary_author, commentary_vcode)
        
        return redirect("/commentary/list/")

    else:
        return render_template('commentary_add.html')

@app.route('/commentary/list/')
def commentary_list():
    auth_info = oauth.getAuthorizedInfo()
    commentary_db = db.Table()
    clist = commentary_db.clist()
    return render_template('commentary_list.html', lists=clist, auth_info=auth_info)

@app.route('/commentary/view/<int:no>')
def commentary_view(no):
    auth_info = oauth.getAuthorizedInfo()
    commentary_db = db.Table()
    cview = commentary_db.cview(no)
    return render_template('commentary_view.html', view=cview, auth_info=auth_info)

@app.route('/commentary/vcode/<int:no>')
def commentary_select_vcode(no):
    auth_info = oauth.getAuthorizedInfo()
    commentary_db = db.Table()
    vclist = commentary_db.vcode(no)
    return render_template('commentary_list.html', lists=vclist, auth_info=auth_info)
