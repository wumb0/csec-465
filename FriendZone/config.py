import os

#get the path that the app is running in
basedir = os.path.abspath(os.path.dirname(__file__))

#get private application resources
f = open(os.path.join(basedir, 'app.vars') , 'r')

CSRF_ENABLED = True
WTF_CSRF_ENABLED = True

#setup database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS=False

#get constants from file
SECRET_KEY = f.readline().strip()
GOOGLE_CONSUMER_KEY = f.readline().strip()
GOOGLE_CONSUMER_SECRET = f.readline().strip()
ELASTICSEARCH_HOST = f.readline().strip()
ELASTICSEARCH_HTTP_AUTH = f.readline().strip().split(":")
BASE_ADMINS = [ x.rstrip() for x in f.readline().split(',') ]
f.close()
