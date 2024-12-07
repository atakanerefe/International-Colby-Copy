from flask import Blueprint, render_template, redirect, url_for, session
from flask import request
from flask_oauthlib.client import OAuth
from website import db, GOOGLE
from .models import User
from flask_login import login_user, login_required, logout_user
import os

# Create a blueprint
auth_blueprint = Blueprint('auth', __name__)

admin_emails = [
        "mbeltguz@colby.edu",
        "aemoreno@colby.edu",
        "mfreese@colby.edu",
        "obraym25@colby.edu"
    ]

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    global GOOGLE
    if request.method == 'POST':
        return GOOGLE.authorize(callback=url_for('authorized', _external=True))
    return 'Hello! Log in with your Google account: <a href="/google-login">Log in</a>'

@auth_blueprint.route('/google-login')
def google_login():
    global GOOGLE
    return GOOGLE.authorize(callback=url_for('auth.authorized', _external=True))

@auth_blueprint.route('/login/authorized')
def authorized():
    global GOOGLE
    response = GOOGLE.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    me = GOOGLE.get('userinfo')
    loginUser(me.data)
    # Here, 'me.data' contains user information.
    # You can perform registration process using this information if needed.
    if me.data['email'] in admin_emails:
        return redirect(url_for('main.admin'))
    return redirect(url_for('main.task'))

def loginUser(userinfo):
    existing_user = User.query.filter_by(email=userinfo['email']).first()
    if not existing_user:
      existing_user = User(email=userinfo['email'])
      db.session.add(existing_user)
      db.session.commit()
    login_user(existing_user)
    # print(existing_user.name)
    # if existing_user.name is None:
    #     print('name is none')
    #     return render_template('name_form.html')

    if existing_user.email in admin_emails:
        return redirect(url_for('main.admin')) 
    
    return redirect(url_for('main.task'))

@auth_blueprint.route('/finish-login')
def finish_login():
    return render_template('name_form.html')

@auth_blueprint.route('/logout')
def logout():
    logout_user()
    session.pop('google_token', None)
    session.clear()
    return redirect(url_for('auth.login'))

@GOOGLE.tokengetter
def get_google_oauth_token():
    return session.get('google_token')