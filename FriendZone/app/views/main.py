from app import db, lm, google, app
from flask import render_template, flash, redirect, session, url_for, Blueprint
from flask.ext.login import login_user, logout_user, current_user, login_required
from app.models import *
#from app.forms import *

@app.errorhandler(404)
def not_found_error(error):
    '''The error handler for invalid pages
    Returns: the rendered 404 template
    '''
    return render_template('404.html')

@app.errorhandler(500)
def internal_error(error):
    '''The error handler for internal errors
    Returns: the rendered 500 template
    '''
    db.session.rollback()
    return render_template('500.html'), 500

@google.tokengetter
def get_google_oauth_token():
    '''Gets a google oauth token
    Returns: the token
    '''
    return session.get('google_token')

@app.route('/login')
def login():
    '''User login page
    Returns: a google authorization handler
    '''
    session.pop('google_token', None)
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template("index.html", title="Home")
