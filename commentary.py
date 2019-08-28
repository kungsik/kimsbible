from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
from kimsbible.lib import vcodeparser as vp
# from kimsbible import oauth
import json
from flask_login import login_user, current_user, login_required

@app.route('/commentary/add/<int:vcode>', methods=['POST','GET'])
@app.route('/commentary/add/', methods=['POST','GET'])
@login_required
def commentary_add(vcode=1):
    if request.method == 'POST':
        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']
        commentary_author = current_user.name
        commentary_email = current_user.user_id

        commentary_db = db.Table()
        commentary_db.add_commentary(commentary_title, commentary_text, commentary_author, commentary_vcode, commentary_email)
        
        return redirect("/commentary/list/")

    else:
        return render_template('commentary_add.html', vcode=vcode)


@app.route('/commentary/edit/<int:no>', methods=['POST','GET'])
@login_required
def commentary_edit(no):
    if request.method == 'POST':
        commentary_db = db.Table()
        if not commentary_db.is_author(no, current_user):
            return redirect("/commentary/view/" + str(no))

        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']

        commentary_db.edit_commentary(no, commentary_title, commentary_text, commentary_vcode)
        
        return redirect("/commentary/view/" + str(no))
    else:
        commentary_db = db.Table()
        if not commentary_db.is_author(no, current_user):
            return redirect("/commentary/view/" + str(no))

        cview = commentary_db.cview(no)

        return render_template('commentary_add.html', cview=cview)


@app.route('/commentary/list/')
def commentary_list():
    commentary_db = db.Table()
    clist = commentary_db.clist()
    return render_template('commentary_list.html', lists=clist, user=current_user)


@app.route('/commentary/view/<int:no>')
def commentary_view(no):
    commentary_db = db.Table()
    cview = commentary_db.cview(no)
    verse = vp.codetostr(cview[6], vp.bookListKor)
    return render_template('commentary_view.html', view=cview, verse=verse)


@app.route('/commentary/vcode/<int:no>')
def commentary_select_vcode(no):
    commentary_db = db.Table()
    vclist = commentary_db.vcode(no)
    return render_template('commentary_list.html', lists=vclist, vcode=no)


@app.route('/commentary/remove/<int:no>')
@login_required
def commentary_del(no):
    commentary_db = db.Table()
    if commentary_db.is_author(no, current_user):
        commentary_db.remove_commentary(no)
        return redirect("/commentary/list/")
    else:
        return redirect("/commentary/list/")