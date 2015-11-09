from app import db, lm, app
from flask import render_template, flash, redirect, session, url_for, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app.models import *
from app.crypto import get_hashstr
from app.forms import *
from datetime import datetime


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated:
        flash("You are already logged in as {}.".format(g.user.email), category="warning")
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        login_user(user, remember=form.remember.data)
        flash("Logged in sucessfully", category='good')
        return redirect(url_for('profile'))
    else:
        for e in form.errors:
            flash(form.errors[e][0], "error")
    return render_template("login.html", title="Login", form=form)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if g.user.is_authenticated:
        flash("You are already logged in as {}.".format(g.user.email), category="warning")
        return redirect(url_for("index"))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=get_hashstr(form.password.data, 'sha512', 100000),
                    name=form.name.data,
                    birthday=form.birthday.data,
                    role=0,
                    bio=form.bio.data,
                    nickname=form.nickname.data,
                    verified=True)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!", category='good')
    else:
        for e in form.errors:
            flash(e + ": " + form.errors[e][0], "error")
    return render_template('signup.html', title="Signup", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template("index.html", title="Home")

@app.route('/profile')
def profile():
    return render_template('profile.html', title='Profile')

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
