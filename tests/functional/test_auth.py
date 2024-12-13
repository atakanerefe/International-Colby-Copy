'''Imports for testing auth'''
from flask_login import current_user, login_user
from website.auth import user_login

def test_login_page(google_client):
    '''Test the login route'''
    response = google_client.get('/login')

    # Check the response is a redirect
    assert response.status_code == 200

    # Check the response contains the login page
    assert b'Log In' in response.data

def test_login_redirect(google_client):
    '''Test the login route'''
    # Test the login-g route
    response = google_client.get('/google_login')

    # Check the response is a redirect to unauthorized page
    assert response.status_code == 500

def test_login_unauthorized(google_client):
    '''Test the authorized route'''
    response = google_client.get('/login/authorized')

    print(response.data)

    # Check that unauthorized access fails
    assert b'Internal Server Error' in response.data


def test_user_login_unknown():
    '''Test the user login process'''
    # create userinfo dictionary
    userinfo = {'email': 'test_user9@example.com'}

    # Call the user_login function
    response = user_login(userinfo)

    # Check the redirect is to the name_form page
    assert 'id' in response

    # Check the user is logged in
    assert current_user is not None

def test_user_login_known(test_client, init_database):
    '''Test the user login process'''
    with test_client.application.app_context():
      # create userinfo dictionary
      userinfo = {'email': 'test_user1@example.com'}

      # Call the user_login function
      user_login(userinfo)

      # Check the redirect is to the home page
      assert current_user is not None


def test_finish_login(google_client):
    '''Test the finish login process'''

    # post to finish-login route
    response = google_client.post('/finish-login', data={'name': 'Test User', 'student_id': '12345', 'email': 'exampleuser6@example.com'})
    
    # Check the redirect is to the home page
    assert response.status_code == 302

    # Check the user is logged in
    assert current_user is not None

    # check the user info is in the database
    assert current_user.name == 'Test User'
    assert current_user.student_id == 12345
    assert current_user.email == 'exampleuser6@example.com'
  
def test_logout(google_client):
    '''Test the logout process'''
    # create logged in user
    login_user(current_user)

    response = google_client.get('/logout')

    # Check the redirect is to the login page
    assert response.status_code == 302

    print(current_user)

    # Check the user is anonymous
    assert current_user.is_anonymous