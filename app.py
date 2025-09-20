from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jacobtube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Flask-Migrate setup

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------------- Models ---------------- #

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    subscriber_count = db.Column(db.Integer, default=0)
    # add other fields like email if you want

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ---------------- Login Manager ---------------- #

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- Routes ---------------- #

@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@app.route('/channel/<int:user_id>')
def channel(user_id):
    user = User.query.get_or_404(user_id)
    user_videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('channel.html', user=user, videos=user_videos)

# ---------------- Run App ---------------- #
if __name__ == '__main__':
    app.run(debug=True)
