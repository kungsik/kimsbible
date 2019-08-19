from kimsbible import app
import os
from flask import Flask, redirect, url_for, session
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "544836946259549"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "dc1d92bdd461c630d0d9ee948dd48c64"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

facebook_bp = make_facebook_blueprint()
app.register_blueprint(facebook_bp, url_prefix="/login")

def getAuthorizedName():
    if 'username' in session:
        return session['username']
    else:
        name = ''
        return name    
    
@app.route("/oauth/facebook/")
def index():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me")
    assert resp.ok, resp.text
    session['username'] = resp.json()["name"]
    return redirect("/commentary/list/")
