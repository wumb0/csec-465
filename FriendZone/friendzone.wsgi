#!/var/www/rc3site/flask/bin/python

from flup.server.fcgi import WSGIServer
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/friendzone/")

from app import app
from app import app as application

if __name__ == '__main__':
	WSGIServer(app).run()
