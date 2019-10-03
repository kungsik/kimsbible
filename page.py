from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
from kimsbible.lib import config

import json
from flask_login import login_user, current_user, login_required
from kimsbible.auth import login_manager

@app.route('/page/add/', methods=['POST','GET'])
@login_required
def page_add():
    if request.method == 'POST' and current_user.user_id == config.admin:
        title = request.form['title']
        content = request.form['content']
        url = request.form['url']

        page_db = db.Page()
        page_db.add_page(title, content, url)

        return redirect("/page/" + url)
        
    else:
        return render_template('page_add.html')


@app.route('/page/<pageurl>/')
def page_view(pageurl):
    page_db = db.Page()
    view = page_db.view_page(pageurl)
    return render_template('page_view.html', pview=view, admin=config.admin)


@app.route('/page/edit/<url>/', methods=['POST','GET'])
@login_required
def page_edit(url):
    if request.method == 'POST' and current_user.user_id == config.admin:
        title = request.form['title']
        content = request.form['content']
        url = request.form['url']

        page_db = db.Page()
        page_db.edit_page(title, content, url)

        return redirect("/page/" + url)
        
    else:
        page_db = db.Page()
        view = page_db.view_page(url)

        return render_template('page_add.html', view=view) 