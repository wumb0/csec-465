from app import db, es
from datetime import datetime
from hashlib import md5
from elasticsearch_dsl import DocType, String, Date, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch, RequestsHttpConnection

connections.add_connection('default', es)

friends_table = db.Table('friends_table',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id')),
)

class User_ES(DocType):
    user_id = Integer(analyzer='snowball')
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    nickname = String(analyzer='snowball')
    email = String(analyzer='snowball')

    def save(self, ** kwargs):
        return super(User_ES, self).save(** kwargs)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    nickname = db.Column(db.String(40))
    email = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.SmallInteger, default=0)
    bio = db.Column(db.String(5000))
    linkname = db.Column(db.String(20), index=True, unique=True)
    birthday = db.Column(db.Date)
    last_seen = db.Column(db.DateTime, default=datetime.now())
    verified = db.Column(db.Boolean, default=0)
    friends_requested = db.relationship('Request', lazy='dynamic', backref='requesting_user', foreign_keys='Request.requesting_user_id')
    friend_requests = db.relationship('Request', lazy='dynamic', backref='requested_user', foreign_keys='Request.requested_user_id')
    posts = db.relationship('Post', lazy='dynamic', primaryjoin="User.id==Post.user_id")
    authored = db.relationship('Post', lazy='dynamic', primaryjoin="User.id==Post.poster_id")
    friends = db.relationship('User',
                              secondary=friends_table,
                              primaryjoin=(friends_table.c.user_id==id),
                              secondaryjoin=(friends_table.c.friend_id == id),
                              lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def is_admin(self):
        if self.role == 1:
            return True
        return False

    def bday_str(self):
        return self.birthday.strftime('%B %-d, %Y')

    def __repr__(self):
        return '<User {}: {}>'.format(self.id, self.name)

    def __str__(self):
        return self.name

    def last_seen_str(self):
        return self.last_seen.strftime('%A, %B %d, %Y %I:%M%p')

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def avatar(self, size):
        '''Generates the gravatar URL for the user
        arg:
            size - the size of the gravatar requested
        Returns: The URL for the user's gravatar
        '''
        return "http://www.gravatar.com/avatar/{0}?d=mm&s={1}".format(md5(self.email).hexdigest(), str(size))

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requesting_user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    requested_user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    def __str__(self):
        return '<Request {} -> {}>'.format(self.requesting_user, self.requested_user)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User, foreign_keys=user_id)
    poster = db.relationship(User, foreign_keys=poster_id)

    def timestamp_str(self):
        return self.timestamp.strftime('%A, %B %d %Y %I:%M%p')

    def __str__(self):
        return self.content[:100]

    def __repr__(self):
        return 'Post: <{}>'.format(self.id)

class Post_ES(DocType):
    post_id = Integer(analyzer='snowball')
    user_id = Integer(analyzer='snowball')
    poster_id = Integer(analyzer='snowball')
    content = String(analyzer='snowball')
    name = String(analyzer='snowball')
    timestamp = Date()

    def save(self, ** kwargs):
        return super(User_ES, self).save(** kwargs)
