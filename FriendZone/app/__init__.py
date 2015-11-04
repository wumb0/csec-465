'''
__init__.py - Initialize the application, logins, and its views
'''
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_oauthlib.client import OAuth
from config import basedir, GOOGLE_CONSUMER_KEY, GOOGLE_CONSUMER_SECRET, \
BASE_ADMINS
from flask.ext.admin import Admin
from flask_admin.base import MenuLink

# Initialize the app and database, import the config
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#setup Google oauth for login
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key= GOOGLE_CONSUMER_KEY,
    consumer_secret= GOOGLE_CONSUMER_SECRET,
    request_token_params={
        'scope' : 'https://www.googleapis.com/auth/userinfo.email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url = None,
    access_token_method = 'POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
)

#create the login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

#this starts the app
from app import models
db.create_all()
db.session.commit()
#TODO: make admin user here
for ad in BASE_ADMINS:
    pass
from app.views import main, admin

#admin setup
#TODO: define admin.py in app/views, define ProtectedIndexView, PostModelView, ProtectedFileAdmin
_admin = Admin(app, 'FriendZone Admin', template_mode='bootstrap3',
              index_view=admin.ProtectedIndexView())
_admin.add_link(MenuLink(name='Back to Site', url='/'))
_admin.add_view(admin.PostModelView())
_admin.add_view(admin.ProtectedFileAdmin(os.path.join(basedir, 'app/static/uploads'), '/static/uploads/', name="Uploads"))

#blueprints are each section of the app
app.register_blueprint(main.main)