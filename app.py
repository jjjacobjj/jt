from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Build the full path to the SQLite database
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'jacobtube.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Example models matching your existing tables
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    subscribers = db.Column(db.Integer)

class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

# Example route to test
@app.route('/')
def index():
    users = User.query.all()
    return '<br>'.join([user.username for user in users])

if __name__ == '__main__':
    app.run(debug=True)
