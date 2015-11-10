'''
__init__.py - Initialize the application, logins, and its views
'''
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_oauthlib.client import OAuth
from config import basedir
from flask.ext.admin import Admin
from flask_admin.base import MenuLink
from flask.ext.elasticsearch import FlaskElasticsearch
from flask_wtf.csrf import CsrfProtect

# Initialize the app and database, import the config
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
es = FlaskElasticsearch()
es.init_app(app)
CsrfProtect(app)

#create the login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

#this starts the app
from app import models
db.create_all()
db.session.commit()
from app.views import main, admin

#admin setup
_admin = Admin(app, 'FriendZone Admin', template_mode='bootstrap3',
              index_view=admin.ProtectedIndexView())
_admin.add_link(MenuLink(name='Back to Site', url='/'))
_admin.add_view(admin.PostModelView(models.Post, db.session))
_admin.add_view(admin.UserModelView(models.User, db.session))
_admin.add_view(admin.ProtectedFileAdmin(os.path.join(basedir, 'app/static/uploads'), '/static/uploads/', name="Uploads"))
