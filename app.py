from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify, render_template, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import db, User
import os
from dotenv import load_dotenv
# werkzeug need to be werkzeug==2.3.7 if getting url error
# uninstall werkzeug and install werkzeug==2.3.7
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres", "postgresql", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

oauth = OAuth(app)

google_redirect_uri = 'http://127.0.0.1:5000/login/authorized' # change to your computer port
# google_redirect_uri = 'https://intapp-f95d32a0df1a.herokuapp.com/login/authorized'

google = oauth.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_CLIENT_ID'),
    consumer_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={'scope': 'email',},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

login_manager = LoginManager(app)
login_manager.login_view = '/'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        loginUser(me.data)
        print(me.data)
        return render_template('task.html')
    return 'Hello! Log in with your Google account: <a href="/login">Log in</a>'

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    me = google.get('userinfo')
    loginUser(me.data)
    # Here, 'me.data' contains user information.
    # You can perform registration process using this information if needed.

    return redirect(url_for('task'))

def loginUser(userinfo):
    existing_user = User.query.filter_by(email=userinfo['email']).first()
    if existing_user:
      login_user(existing_user)
    else:
      new_user = User(email=userinfo['email'])
      db.session.add(new_user)
      db.session.commit()
      login_user(new_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('google_token', None)
    return redirect(url_for('index'))
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/task')
@login_required
def task():
    return render_template('task.html')

@app.route('/subtask')
@login_required
def subtask():
    return render_template('subtask.html')

@app.route('/steps')
@login_required
def steps():
    step = request.args.get('step', default=1, type=int)
    return render_template('steps.html', active_step=step)

@app.route('/admin')
@login_required
def admin():
    return render_template('admin_home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
    app.run(debug=True)