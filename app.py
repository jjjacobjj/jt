from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_migrate import Migrate   # ✅ NEW
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)   # ✅ NEW

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ---------------------------
# MODELS
# ---------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    # ✅ NEW COLUMN
    subscriber_count = db.Column(db.Integer, default=0)  

    videos = db.relationship('Video', backref='author', lazy=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# ---------------------------
# LOGIN MANAGER
# ---------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------
# ROUTES
# ---------------------------
@app.route('/')
def home():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        flash("Invalid credentials")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        url = request.form['url']

        video = Video(title=title, description=description, url=url, author=current_user)
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('upload.html')


@app.route('/channel/<int:user_id>')
def channel(user_id):
    user = User.query.get_or_404(user_id)
    videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('channel.html', user=user, videos=videos)


# ---------------------------
# RUN LOCALLY
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
