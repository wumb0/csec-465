from app import db
from datetime import datetime
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    nickname = db.Column(db.String(40))
    email = db.Column(db.String(100), index=True)
    role = db.Column(db.SmallInteger, default=0)
    bio = db.Column(db.String(5000))
    birthday = db.Column(db.Date)
    last_seen = db.Column(db.DateTime, default=datetime.now())
    friends = db.relationship('User')
    posts = db.relationship('Post', backref = "user", lazy='dynamic')

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
        return self.last_seen.strftime('%A, %B %d %Y %I:%M%p')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime, defaule=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def timestamp_str(self):
        return self.timestamp.strftime('%A, %B %d %Y %I:%M%p')

    def __str__(self):
        return self.content[:100]

    def __repr__(self):
        return 'Post: <{}>'.format(self.id)
