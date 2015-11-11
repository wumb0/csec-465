from app import db, lm, app, es
from flask import render_template, flash, redirect, session, url_for, g, abort, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app.models import *
from app.crypto import get_hashstr
from app.forms import *
from datetime import datetime
from sqlalchemy import desc
import json


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
        user_es = User_ES(user_id=user.id, email=form.email.data,
                    name=form.name.data,
                    linkname=form.linkname.data,
                    nickname=form.nickname.data
                    );
        user_es.save()
        try:
            logout_user()
            session.clear()
        except: pass
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
        data = json.loads(request.get_data())
        req = Request.query.filter_by(id=data['id']).one()
    except:
        try:
            user = User.query.filter_by(id=data['id']).one()
            if data['action'] == "del_fr":
                g.user.friends.remove(user)
                user.friends.remove(g.user)
                db.session.commit()
                return "", 200
            elif data['action'] == "add_fr" and user not in g.user.friends:
                req = Request(requesting_user_id=g.user.id, requested_user_id=user.id)
                db.session.add(req)
                db.session.commit()
                return "", 200
        except:
            return "", 400
    if data['action'] == "add_req" and req.requested_user_id == g.user.id:
        g.user.friends.append(req.requesting_user)
        req.requesting_user.friends.append(g.user)
        db.session.add(req.requesting_user)
        db.session.add(g.user)
        db.session.delete(req)
    elif data['action'] == "del_req" and req.requested_user_id == g.user.id:
        db.session.delete(req)
    elif data['action'] == "del_reqd" and req.requesting_user_id == g.user.id:
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

@app.route('/profile')
def profile():
    return redirect(url_for('user_profile', linkname=g.user.linkname))

@app.route('/api/posts', methods=['POST'])
@login_required
def posts_api():
    try:
        data = json.loads(request.get_data())
        post = Post.query.filter_by(id=data['id']).one()
        if data['action'] == "del_post" and (g.user == post.poster or g.user == post.user):
            s = Post_ES.search()
            s = s.query('match', post_id=post.id)
            results = s.execute()
            for es_post in results:
                es_post.delete()
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
        if g.user in user.friends or g.user == user:
            post = Post(content=post_form.content.data,
                        timestamp=datetime.now(),
                        user_id=user.id,
                        poster_id=g.user.id)
            db.session.add(post)
            db.session.commit()
            post_es = Post_ES(post_id = post.id,
                            user_id = user.id,
                            user_linkname = user.linkname,
                            user_name = user.name,
                            poster_id = g.user.id,
                            poster_linkname = user.linkname,
                            content = post_form.content.data,
                            name = post.timestamp)
            post_es.save()
        else:
            flash("You cannot post here, you are not friends with " + user.name, category='error')
        post_form.content.data = ""
    return render_template('profile.html', title='Profile', user=user, post_form=post_form, posts=posts)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        if form.search_type.data == "Posts":
            s = Post_ES.search()
            s = s.query('match', content = form.query.data)
            results = s.execute()
        elif form.search_type.data == "Users":
            s = User_ES.search()
            s = s.query('match', name=form.query.data)
            results = s.execute()
        else:
            abort(400)
    return render_template('search.html', title="Search", form=form, results=results, results_type=form.search_type.data)

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
