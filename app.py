from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jacobtube.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ===================== MODELS =====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscriber_count = db.Column(db.Integer, default=0)  # added subscriber_count

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ===================== LOGIN HANDLERS =====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===================== ROUTES =====================
@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/channel/<int:user_id>')
def channel(user_id):
    user = User.query.get_or_404(user_id)
    videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('channel.html', user=user, videos=videos)

@app.route('/watch/<int:video_id>')
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    return render_template('watch.html', video=video)

if __name__ == "__main__":
    app.run(debug=True)
