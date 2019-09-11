from flask import Flask, send_from_directory, request
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/robots.txt')
def robot_to_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.after_request
def set_response_headers(r):
    r.headers['Cache-Control'] = 'public, max-age=3600'
    return r


import kimsbible.bhsheb
import kimsbible.bhsheb_conjugator
import kimsbible.bhsheb_stat
import kimsbible.bhsheb_search
import kimsbible.sblgnt
import kimsbible.auth
#import kimsbible.bhsheb_tfidf
import kimsbible.commentary
#import kimsbible.oauth
import kimsbible.studytools
