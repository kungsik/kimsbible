from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
from kimsbible.lib import vcodeparser as vp
# from kimsbible import oauth
import json
from flask_login import login_user, current_user, login_required

@app.route('/<table>/add/<int:vcode>/', methods=['POST','GET'])
@app.route('/<table>/add/', methods=['POST','GET'])
@login_required
def commentary_add(table, vcode=1):
    if request.method == 'POST':
        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']
        commentary_copen = int(request.form['copen'])
        commentary_author = current_user.name
        commentary_email = current_user.user_id
        return_vcode_page = request.form['return_vcode_page']

        commentary_db = db.Table()
        commentary_db.add_commentary(table, commentary_title, commentary_text, commentary_author, commentary_vcode, commentary_email, commentary_copen)
        
        if return_vcode_page:
            return redirect("/commentary/vcode/" + str(return_vcode_page))
        else:
            return redirect("/" + table + "/list/")

    else:
        return render_template('commentary_add.html', vcode=vcode, table=table)


@app.route('/<table>/edit/<int:no>/', methods=['POST','GET'])
@login_required
def commentary_edit(table, no):
    if request.method == 'POST':
        commentary_db = db.Table()
        if not commentary_db.is_author(table, no, current_user):
            return redirect("/" + table + "/view/" + str(no))

        commentary_title = request.form['commentary_title']
        commentary_text = request.form['commentary_text']
        commentary_vcode = request.form['commentary_vcode']
        commentary_copen = int(request.form['copen'])

        commentary_db.edit_commentary(table, no, commentary_title, commentary_text, commentary_vcode, commentary_copen)
        
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

    return render_template('commentary_list.html', lists=clist, user=current_user, table=table, totalpage=totalpage, pagenum=pagenum, category='list')


@app.route('/commentary/mylist/', methods=['POST', 'GET'])
@login_required
def commentary_mylist():
    if request.method == 'GET':
        pagenum = request.args.get('p')
    
    if not pagenum:
        pagenum = 1

    commentary_db = db.Table()
    clist = commentary_db.myclist('commentary', pagenum, current_user.user_id)
    totalnum = commentary_db.get_table_count('commentary')
    totalpage = int(int(totalnum) / 11) + 1

    return render_template('commentary_list.html', lists=clist, user=current_user, table='commentary', totalpage=totalpage, pagenum=pagenum, category='mylist')



@app.route('/<table>/view/<int:no>/<title>/', methods=['POST', 'GET'])
@app.route('/<table>/view/<int:no>/', methods=['POST', 'GET'])
def commentary_view(table, no, title=''):

    if request.method == 'GET':
        mode  = request.args.get('mode')
        pagenum = request.args.get('p')
        vcode = request.args.get('v')
    else:
        mode = ''
        pagenum = ''
        vcode = ''

    commentary_db = db.Table()
    cview = commentary_db.cview(table, no)

    # 비공개 글일 경우 해당 저자가 아니면 리스트 목록으로 넘어감
    try:
        if cview[13] == 0 and current_user.user_id != cview[3]:
            return redirect('/' + table + '/list/')
    except:
        return redirect('/' + table + '/list/')
    else:
        return render_template('commentary_view.html', view=cview, table=table, mode=mode, pagenum=pagenum, vcode=vcode)


@app.route('/commentary/vcode/<int:no>/', methods=['POST', 'GET'])
def commentary_select_vcode(no):
    commentary_db = db.Table()
    try:
        if current_user.user_id:
            vclist = commentary_db.vcode_mylist(no, current_user.user_id)
            category = 'myvcode'
    except:
        vclist = commentary_db.vcode_list(no)
        category = 'vcode'
    
    return render_template('commentary_list.html', lists=vclist, vcode=no, pagenum=1, totalpage=1, category=category)


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

