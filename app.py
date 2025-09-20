from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jacobtube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'videos')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --------- MODELS ---------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    subscriber_count = db.Column(db.Integer, default=0)
    videos = db.relationship('Video', backref='uploader', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password is not readable!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --------- LOGIN LOADER ---------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------- ROUTES ---------
@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/channel/<int:user_id>')
def channel(user_id):
    user = User.query.get_or_404(user_id)
    videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('channel.html', user=user, videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            video = Video(title=title, filename=filename, user_id=current_user.id)
            db.session.add(video)
            db.session.commit()
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('upload.html')

# --------- RUN APP ---------
if __name__ == '__main__':
    # Create DB tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
