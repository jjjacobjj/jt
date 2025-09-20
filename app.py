from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jakyupiohljknmhkjiuoyhujknmhjyuihonpjkyhkjulihjy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jacobtube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/videos'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ----------------- Models -----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscribers = db.Column(db.Integer, default=0)

    def get_id(self):
        return str(self.id)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ----------------- User loader -----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- Routes -----------------
@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos, current_user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Incorrect username or password")
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        file = request.files['file']
        if file:
            filename = file.filename
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            new_video = Video(title=title, description=description, filename=filename, user_id=current_user.id)
            db.session.add(new_video)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/watch/<int:video_id>', methods=['GET', 'POST'])
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form['comment']
        new_comment = Comment(content=content, video_id=video.id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
    comments = Comment.query.filter_by(video_id=video.id).all()
    return render_template('watch.html', video=video, comments=comments, current_user=current_user)

@app.route('/channel/<int:user_id>')
def channel(user_id):
    user = User.query.get_or_404(user_id)
    videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('channel.html', user=user, videos=videos, current_user=current_user)

# ----------------- Initialize DB -----------------
with app.app_context():
    db.create_all()

# ----------------- Run app -----------------
if __name__ == "__main__":
    app.run(debug=True)
