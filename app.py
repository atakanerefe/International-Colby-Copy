from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from models import db, User
# werkzeug need to be werkzeug==2.3.7 if getting url error
# uninstall werkzeug and install werkzeug==2.3.7

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsecretkey207'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

oauth = OAuth(app)

google_client_id = 'REMOVED_CLIENT_ID'
google_client_secret = 'REMOVED_CLIENT_SECRET'
google_redirect_uri = 'http://127.0.0.1:5000/login/authorized' # change to your computer port

google = oauth.remote_app(
    'google',
    consumer_key=google_client_id,
    consumer_secret=google_client_secret,
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
        return jsonify({'data': me.data}) # redirect to the main (task) page instead
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

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))\
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
    app.run(debug=True)