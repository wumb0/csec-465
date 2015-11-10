from app import db, lm, app, es
from flask import render_template, flash, redirect, session, url_for, g, abort
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
                    linkname=form.linkname.data,
                    bio=form.bio.data,
                    nickname=form.nickname.data,
                    verified=True)
        db.session.add(user)
        db.session.commit()
        user_es = User_ES(user_id=user.id, email=form.email.data,
                    name=form.name.data,
                    linkname=form.linkname.data,
                    nickname=form.nickname.data
                    );
        user_es.save()
        flash("Registered successfully!", category='good')
        return redirect(url_for('login'))
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

@app.route('/friends')
@login_required
def friends():
    return render_template("friends.html", title="Friends")

@app.route('/api/requests', methods=["POST"])
def api_requests():
    '''
    Case1: user accepts request. delete request and add friends
    Case2: user deletes request. delete request only.
    Case3: requesting user deletes request. delete request only
    '''
    pass

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template("index.html", title="Home")

@app.route('/testfriend')
def testfriend():
    user = User.query.filter_by(id=2).one()
    req = Request(requesting_user_id=g.user.id, requested_user_id=user.id)
    db.session.add(req)
    db.session.commit()

@app.route('/testesindex')
def testesindex():
    user = User_ES(user_id=1, email='dad@dad.com', name='dad', linkname='dad', nickname='dad')
    user.save()
    s = User_ES.search();
    s = s.query('match', user_id=1)
    results = s.execute()
    for user in results:
        return user.email

@app.route('/testes_search')
def testes_search():
    s = User_ES.search();
    s = s.query('match', user_id=1)
    results = s.execute()
    last = ''
    for user in results:
        last = user.email
        print user.email
    return last


@app.route('/testesfriend')
def testesfriend():
    s = User_ES.search()
    s = s.filter('term').query('match', id = 1)
    results = s.execute()
    for user in results:
        return user.name

@app.route('/listreq')
def listfriend():
    print g.user.friends_requested.all()
    print g.user.friend_requests.all()

@app.route('/acceptfriend')
def acceptfriend():
    reqs = g.user.friend_requests.all()
    for req in reqs:
        g.user.friends.append(req.requesting_user)
        req.requesting_user.friends.append(g.user)
        db.session.delete(req)
    db.session.add(g.user)
    db.session.commit()
    print g.user.friends.all()


@app.route('/testpost')
def testpost():
    post = Post(content="Are you my dad?? More at 11.",
                user_id=1,
                poster_id=g.user.id)
    db.session.add(post)
    db.session.commit()

@app.route('/profile')
def profile():
    return render_template('profile.html', title='Profile', user=g.user)

@app.route('/<linkname>/profile')
@login_required
def user_profile(linkname):
    try:
        user = User.query.filter_by(linkname=linkname).one()
    except:
        abort(404)
    return render_template('profile.html', title='Profile', user=user)

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
