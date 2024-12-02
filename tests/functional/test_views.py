def test_home_page_without_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing, user not logged in
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Log' in response.data
    assert b'in' in response.data
    assert b'Google' in response.data


def test_home_page_with_login(test_client, login_user, init_database):
    """
    GIVEN a Flask application configured for testing, user logged in
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Tasks' in response.data

def test_subtask_page_without_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing, user not logged in
    WHEN the '/subtask' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/subtask', follow_redirects=True)
    assert response.status_code == 200
    assert b'Log' in response.data
    assert b'in' in response.data
    assert b'Google' in response.data

def test_subtask_page_with_login(test_client, login_user, init_database):
    """
    GIVEN a Flask application configured for testing, user logged in
    WHEN the '/subtask' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/subtask', follow_redirects=True)
    assert response.status_code == 200
    assert b'Subtasks' in response.data

def test_steps_page_without_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing, user not logged in
    WHEN the '/steps' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/steps', follow_redirects=True)
    assert response.status_code == 200
    assert b'Log' in response.data
    assert b'in' in response.data
    assert b'Google' in response.data

def test_steps_page_with_login(test_client, login_user, init_database):
    """
    GIVEN a Flask application configured for testing, user logged in
    WHEN the '/steps' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/steps', follow_redirects=True)
    assert response.status_code == 200
    assert b'Step' in response.data

def test_admin_page_without_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing, user not logged in
    WHEN the '/admin' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b'Log' in response.data
    assert b'in' in response.data
    assert b'Google' in response.data

def test_admin_page_with_login(test_client, login_user, init_database):
    """
    GIVEN a Flask application configured for testing, user logged in
    WHEN the '/admin' page is requested (GET)
    THEN check the response is valid
    """
    init_database(test_client)
    response = test_client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b'Welocome' in response.data
    assert b'Admin' in response.data

def test_admin_addTask(test_client, init_database):
    init_database(test_client)
    # Not sure how to target text to specific text box