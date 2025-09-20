from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

# Make sure the instance folder exists
if not os.path.exists('instance'):
    os.makedirs('instance')

# SQLite database path
db_path = os.path.join('instance', 'jt.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('videos', lazy=True))

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

if __name__ == '__main__':
    app.run(debug=True)
