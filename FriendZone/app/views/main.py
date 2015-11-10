from app import db, lm, app
from flask import render_template, flash, redirect, session, url_for, g, abort, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app.models import *
from app.crypto import get_hashstr
from app.forms import *
from datetime import datetime
from sqlalchemy import desc


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now()
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

@app.route('/api/friends', methods=["POST"])
@login_required
def friends_api():
    '''
    Case1: user accepts request. delete request and add friends
    Case2: user deletes request. delete request only.
    Case3: requesting user deletes request. delete request only
    Case4: user deletes a user from their friends list
    '''
    try:
        data = request.get_data()
        key, id = data.split("-")
        req = Request.query.filter_by(id=id).one()
    except:
        try:
            user = User.query.filter_by(id=id).one()
            if key == "del_fr":
                g.user.friends.remove(user)
                user.friends.remove(g.user)
                db.session.commit()
                return "", 200
            elif key == "add_fr" and user not in g.user.friends:
                req = Request(requesting_user_id=g.user.id, requested_user_id=user.id)
                db.session.add(req)
                db.session.commit()
                return "", 200
        except:
            return "", 400
    if key == "add_req" and req.requested_user_id == g.user.id:
        g.user.friends.append(req.requesting_user)
        req.requesting_user.friends.append(g.user)
        db.session.add(req.requesting_user)
        db.session.add(g.user)
        db.session.delete(req)
    elif key == "del_req" and req.requested_user_id == g.user.id:
        db.session.delete(req)
    elif key == "del_reqd" and req.requesting_user_id == g.user.id:
        db.session.delete(req)
    else:
        return "", 400
    db.session.commit()
    return "", 200

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template("index.html", title="Home")

@app.route('/testpost')
def testpost():
    post = Post(content="Are you my dad?? More at 11.",
                user_id=1,
                poster_id=g.user.id)
    db.session.add(post)
    db.session.commit()

@app.route('/profile')
def profile():
    return redirect(url_for('user_profile', linkname=g.user.linkname))

@app.route('/api/posts', methods=['POST'])
@login_required
def posts_api():
    try:
        key, id = request.get_data().split("-")
        post = Post.query.filter_by(id=id).one()
        if key == "del_post" and (g.user == post.poster or g.user == post.user):
            db.session.delete(post)
            db.session.commit()
            return "", 200
    except:
        pass
    return "", 400

@app.route('/<linkname>/profile', methods=['POST', 'GET'])
@login_required
def user_profile(linkname):
    try:
        user = User.query.filter_by(linkname=linkname).one()
    except:
        abort(404)
    posts = Post.query.filter_by(user_id=user.id).order_by(desc(Post.timestamp))
    post_form = PostForm()
    if post_form.validate_on_submit():
        post = Post(content=post_form.content.data,
                    timestamp=datetime.now(),
                    user_id=user.id,
                    poster_id=g.user.id)
        db.session.add(post)
        db.session.commit()
    return render_template('profile.html', title='Profile', user=user, post_form=post_form, posts=posts)

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
