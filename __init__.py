from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

import kimsbible.views
import kimsbible.conjugator
import kimsbible.stat
import kimsbible.search
import kimsbible.tfidf
