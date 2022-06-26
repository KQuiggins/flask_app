from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db.db import db



# create a blog post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    post_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Blog post ' + str(self.id)


# Create a class to represent the user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    password_hash = db.Column(db.String(120))
    profile_pic = db.Column(db.String(200), nullable=True)
    posts = db.relationship('Post', backref='poster', lazy=True)

    @ property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @ password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return '<Name: {}>'.format(self.name)