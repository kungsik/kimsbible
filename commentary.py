from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
from kimsbible.lib import vcodeparser as vp
# from kimsbible import oauth
import json
from flask_login import login_user, current_user, login_required

@app.route('/<table>/add/<int:vcode>', methods=['POST','GET'])
@app.route('/<table>/add/', methods=['POST','GET'])
@login_required
def commentary_add(table, vcode=1):
    if request.method == 'POST':
        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']
        commentary_author = current_user.name
        commentary_email = current_user.user_id

        commentary_db = db.Table()
        commentary_db.add_commentary(table, commentary_title, commentary_text, commentary_author, commentary_vcode, commentary_email)
        
        return redirect("/" + table + "/list/")

    else:
        return render_template('commentary_add.html', vcode=vcode, table=table)


@app.route('/<table>/edit/<int:no>', methods=['POST','GET'])
@login_required
def commentary_edit(table, no):
    if request.method == 'POST':
        commentary_db = db.Table()
        if not commentary_db.is_author(table, no, current_user):
            return redirect("/" + table + "/view/" + str(no))

        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']

        commentary_db.edit_commentary(table, no, commentary_title, commentary_text, commentary_vcode)
        
        return redirect("/" + table + "/view/" + str(no))
    else:
        commentary_db = db.Table()
        if not commentary_db.is_author(table, no, current_user):
            return redirect("/" + table + "/view/" + str(no))

        cview = commentary_db.cview(table, no)

        return render_template('commentary_add.html', cview=cview, table=table)


@app.route('/commentary/intro/')
def commentary_intro():
    return render_template('commentary_intro.html')

@app.route('/<table>/list/', methods=['POST', 'GET'])
def commentary_list(table):
    if request.method == 'GET':
        pagenum = request.args.get('p')
    
    if not pagenum:
        pagenum = 1

    commentary_db = db.Table()
    clist = commentary_db.clist(table, pagenum)
    totalnum = commentary_db.get_table_count(table)
    totalpage = int(int(totalnum) / 11) + 1

    return render_template('commentary_list.html', lists=clist, user=current_user, table=table, totalpage=totalpage, pagenum=pagenum)



@app.route('/<table>/view/<int:no>/<title>/')
@app.route('/<table>/view/<int:no>/')
def commentary_view(table, no, title=''):
    commentary_db = db.Table()
    cview = commentary_db.cview(table, no)
    return render_template('commentary_view.html', view=cview, table=table)


@app.route('/commentary/vcode/<int:no>')
def commentary_select_vcode(no):
    commentary_db = db.Table()
    vclist = commentary_db.vcode_list(no)
    return render_template('commentary_list.html', lists=vclist, vcode=no)


@app.route('/<table>/remove/confirm/<int:no>')
@login_required
def confirm_remove(table, no):
    return render_template('commentary_confirm_remove.html', no=no, table=table)


@app.route('/<table>/remove/<int:no>')
@login_required
def commentary_del(table, no):
    commentary_db = db.Table()
    if commentary_db.is_author(table, no, current_user):
        commentary_db.remove_commentary(table, no)
        return redirect("/" + table + "/list/")
    else:
        return redirect("/" + table + "/list/")

@app.route('/commentary/vcode/')
def vcode_tutorial():
    return render_template('commentary_vcode_tutorial.html')

