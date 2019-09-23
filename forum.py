from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
import json
from flask_login import login_user, current_user, login_required
from kimsbible.auth import login_manager

forum_db = db.Forum()

@app.route('/forum/add/', methods=['POST','GET'])
@login_required
def topic_add():
    if request.method == 'POST':
        topic = request.form['topic']
        content = request.form['content']
        author = current_user.name
        email = current_user.user_id

        forum_db.add_topic(topic, content, author, email)

        return redirect("/forum/list")
        
    else:
        return render_template('forum_add_topic.html')


@app.route('/forum/list/')
def topic_list():
    lists = forum_db.list_topic()
    return render_template('forum_list_topic.html', lists=lists)


@app.route('/forum/view/<no>')
def topic_view(no):
    view = forum_db.view_topic(no)
    reply_list = forum_db.view_reply(no)
    return render_template('forum_view_topic.html', view=view, reply_list=reply_list)

@app.route('/forum/addreply/<topic_no>', methods=['POST','GET'])
@login_required
def add_reply(topic_no):
    if request.method == 'POST':
        content = request.form['content']
        author = current_user.name
        email = current_user.user_id

        forum_db.add_reply(topic_no, content, author, email)

        return redirect("/forum/view/" + topic_no)
        
    else:
        return render_template('forum_add_reply.html') 

@app.route('/forum/edit/<int:no>', methods=['POST','GET'])
@login_required
def topic_edit(no):
    if request.method == 'POST':
        dbdata = db.Table()
        if not dbdata.is_author('forum', no, current_user):
            return redirect("/")

        topic = request.form['topic']
        content = request.form['content']

        forum_db.edit(no, topic, content)

        if forum_db.get_topicid(no):
            topicid = forum_db.get_topicid(no)
        else:
            topicid = no
        
        return redirect("/forum/view/" + str(topicid))
    else:
        dbdata = db.Table()
        if not dbdata.is_author('forum', no, current_user):
            return redirect("/")

        view = forum_db.view_topic(no)
        no = view[0]
        topic = view[3]
        content = view[4]

        return render_template('forum_add_topic.html', topic=topic, content=content, no=no)


@app.route('/forum/remove/<int:no>', methods=['POST','GET'])
@login_required
def topic_remove(no):
    dbdata = db.Table()
    if not dbdata.is_author('forum', no, current_user):
        return redirect("/")

    forum_db.remove_topic(no)

    return redirect("/forum/list")