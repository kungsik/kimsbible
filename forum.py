from flask import render_template, request, url_for, redirect, session
from kimsbible import app
from kimsbible.lib import db
import json
from flask_login import login_user, current_user, login_required
from kimsbible.auth import login_manager

@app.route('/forum/add/', methods=['POST','GET'])
@login_required
def topic_add():
    if request.method == 'POST':
        topic = request.form['topic']
        content = request.form['content']
        author = current_user.name
        email = current_user.user_id

        forum_db = db.Forum()
        forum_db.add_topic(topic, content, author, email)

        return redirect("/forum/list")
        
    else:
        return render_template('forum_add_topic.html')


@app.route('/forum/list/')
def topic_list():
    forum_db = db.Forum()
    lists = forum_db.list_topic()
    return render_template('forum_list_topic.html', lists=lists)


@app.route('/forum/view/<no>/')
def topic_view(no):
    forum_db = db.Forum()
    view = forum_db.view_topic(no)
    reply_list = forum_db.view_reply(no)

    # 이메일 공개/비공개
    user_db = db.User()
    identity = user_db.get_identity(view[2])

    # reply 리스트 이메일 공개/비공개 체크
    if reply_list:
        reply_identity = []
        for reply in reply_list:
            reply_identity.append(user_db.get_identity(reply[2]))       
    else:
        reply_identity = []

    return render_template('forum_view_topic.html', fview=view, reply_list=reply_list, identity=identity, reply_identity=reply_identity)

@app.route('/forum/addreply/<topic_no>/', methods=['POST','GET'])
@login_required
def add_reply(topic_no):
    if request.method == 'POST':
        content = request.form['content']
        author = current_user.name
        email = current_user.user_id

        forum_db = db.Forum()
        forum_db.add_reply(topic_no, content, author, email)

        return redirect("/forum/view/" + topic_no)
        
    else:
        return render_template('forum_add_reply.html') 

@app.route('/forum/edit/<int:no>/', methods=['POST','GET'])
@login_required
def topic_edit(no):
    if request.method == 'POST':
        user_db = db.User()
        if not user_db.is_author('forum', no, current_user):
            return redirect("/")

        topic = request.form['topic']
        content = request.form['content']

        forum_db = db.Forum()
        forum_db.edit(no, topic, content)

        if forum_db.get_topicid(no):
            topicid = forum_db.get_topicid(no)
        else:
            topicid = no
        
        return redirect("/forum/view/" + str(topicid))
    else:
        user_db = db.User()
        if not user_db.is_author('forum', no, current_user):
            return redirect("/")

        forum_db = db.Forum()
        view = forum_db.view_topic(no)
        no = view[0]
        topic = view[3]
        content = view[4]

        return render_template('forum_add_topic.html', topic=topic, content=content, no=no)


@app.route('/forum/remove/<int:no>/', methods=['POST','GET'])
@login_required
def topic_remove(no):
    user_db = db.User()
    if not user_db.is_author('forum', no, current_user):
        return redirect("/")

    forum_db = db.Forum()
    forum_db.remove_topic(no)

    return redirect("/forum/list")