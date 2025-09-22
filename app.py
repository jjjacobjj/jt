import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize app
app = Flask(__name__)

# --- Database setup ---
# Use PostgreSQL if DATABASE_URL is provided (Render), otherwise fallback to SQLite
if os.getenv("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db + migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    videos = db.relationship("Video", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="video", lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subscriber_count = db.Column(db.Integer, default=0)


# --- Routes ---
@app.route("/")
def index():
    users = User.query.all()
    videos = Video.query.all()
    comments = Comment.query.all()
    subscriptions = Subscription.query.all()
    return render_template(
        "index.html",
        users=users,
        videos=videos,
        comments=comments,
        subscriptions=subscriptions,
    )


# --- Database create helper ---
@app.before_first_request
def create_tables():
    db.create_all()


# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)
