from kimsbible import app
import os
from flask import Flask, redirect, url_for, session
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "544836946259549"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "dc1d92bdd461c630d0d9ee948dd48c64"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

facebook_bp = make_facebook_blueprint(
    redirect_url="/oauth/facebook/"
)
app.register_blueprint(
    facebook_bp, 
    url_prefix="/login",
    )

def getAuthorizedInfo():
    result = '<div id="authorized" style="text-align: right">'
    if 'username' in session:
        result += '<img src="/static/img/' + session['oauth_source'] + '.png" height="18px" width="18px">' + session['username'] + ' (<a href="/oauth/logout/">로그아웃</a>)</div>'
        return result
    else:
        result += '<a href="/oauth/facebook/"><img src="/static/img/facebook.png" height="30px" width="30px"></a></div>'
        return result
    
@app.route("/oauth/facebook/")
def oauth_facebook():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me")
    assert resp.ok, resp.text
    session['username'] = resp.json()["name"]
    session['oauth_source'] = 'facebook'
    return redirect("/commentary/list/")

@app.route("/oauth/logout/")
def logout():
    session.clear()
    return redirect("/commentary/list/") 