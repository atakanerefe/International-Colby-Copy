# The implementation Al Madi and us came up with requires global GOOGLE
# pylint: disable=global-variable-not-assigned
'''Uses flask to manage user login, logout, and flow. 
Uses Google OAuth2 for login.'''
from flask import Blueprint, render_template, redirect, url_for, session
from flask import request
from flask_login import login_user, logout_user
from website import db, GOOGLE
from .models import User

# Create a blueprint
auth_blueprint = Blueprint('auth', __name__)

admin_emails = [
        "mbeltguz@colby.edu",
        "aemoreno@colby.edu",
        "mfreese@colby.edu",
        # "obraym25@colby.edu"
    ]

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''Login page'''
    global GOOGLE
    if request.method == 'POST':
        return GOOGLE.authorize(callback=url_for('authorized', _external=True))
    return 'Hello! Log in with your Google account: <a href="/google-login">Log in</a>'

@auth_blueprint.route('/google-login')
def google_login():
    '''Redirect to Google login page'''
    global GOOGLE
    return GOOGLE.authorize(callback=url_for('auth.authorized', _external=True))

@auth_blueprint.route('/login/authorized')
def authorized():
    '''Callback page after Google login. Calls loginUser() to finish login process.'''
    global GOOGLE
    response = GOOGLE.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    me = GOOGLE.get('userinfo')
    return user_login(me.data)
    # Here, 'me.data' contains user information.
    # You can perform registration process using this information if needed.

def user_login(userinfo):
    '''Finish login process. If user is not registered, redirect to name_form.html.'''
    email = userinfo['email']
    existing_user = User.query.filter_by(email=email).first()
    print(existing_user)
    if not existing_user or existing_user.student_id is None:
        print('no existing user')
        return render_template('name_form.html', email=email)
    login_user(existing_user)
    # print(existing_user.name)
    # if existing_user.name is None:
    #     print('name is none')
    #     return render_template('name_form.html')

    if existing_user.email in admin_emails:
        return redirect(url_for('main.admin'))

    return redirect(url_for('main.task'))

@auth_blueprint.route('/finish-login', methods = ['POST'])
def finish_login():
    '''Finish registration process. Add user to database with all information.'''
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form['student_id']
        email = request.form['email']
        new_user = User.query.filter_by(email=email).first()
        if not new_user:
            new_user = User(name=name, email=email, student_id=student_id)
        else:
            new_user.name = name
            new_user.student_id = student_id
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

    return redirect(url_for('main.home'))

@auth_blueprint.route('/logout')
def logout():
    '''Logout page'''
    logout_user()
    session.pop('google_token', None)
    session.clear()
    return redirect(url_for('auth.login'))

@GOOGLE.tokengetter
def get_google_oauth_token():
    '''Get Google token'''
    return session.get('google_token')
