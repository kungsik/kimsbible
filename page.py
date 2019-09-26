from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
import json
from flask_login import login_user, current_user, login_required
from kimsbible.auth import login_manager

@app.route('/page/add/', methods=['POST','GET'])
@login_required
def page_add():
    if request.method == 'POST' and current_user.user_id == 'kks@alphalef.com':
        title = request.form['title']
        content = request.form['content']

        page_db = db.Page()
        page_db.add_page(title, content)

        return redirect("/page/" + title)
        
    else:
        return render_template('page_add.html')


@app.route('/page/<title>')
def page_view(title):
    page_db = db.Page()
    page = page_db.view_page(title)
    return render_template('page_view.html', page=page)


@app.route('/page/edit/<title>', methods=['POST','GET'])
@login_required
def topic_edit(no):
    if request.method == 'POST' and current_user.user_id == 'kks@alphalef.com':
        title = request.form['title']
        content = request.form['content']

        page_db = db.Page()
        page_db.add_page(title, content)

        return redirect("/page/" + title)
        
    else:
        dbdata = db.Table()
        if not dbdata.is_author('forum', no, current_user):
            return redirect("/")

        forum_db = db.Forum()
        view = forum_db.view_topic(no)
        no = view[0]
        topic = view[3]
        content = view[4]

        return render_template('forum_add_topic.html', topic=topic, content=content, no=no)