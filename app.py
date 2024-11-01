from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify, render_template, jsonify
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from models import db, User
import os
from dotenv import load_dotenv
# werkzeug need to be werkzeug==2.3.7 if getting url error
# uninstall werkzeug and install werkzeug==2.3.7

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

oauth = OAuth(app)

google_redirect_uri = 'http://127.0.0.1:5000/login/authorized' # change to your computer port

load_dotenv()

google = oauth.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_CLIENT_ID'),
    consumer_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return render_template('subTask.html')
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
    # Here, 'me.data' contains user information.
    # You can perform registration process using this information if needed.

    return redirect(url_for('subTask'))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/subTask')
def subTasks():
    return render_template('subTask.html')

@app.route('/steps')
def steps():
    step = request.args.get('step', default=1, type=int)
    return render_template('steps.html', active_step=step)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
    app.run(debug=True)