import pytest
from flask import url_for
from unittest.mock import MagicMock
from website.models import User, Task, Subtask, Progress, Step, Tag
from website.views import get_subtask_status_by_progress
from website import db

admin_emails = [
        "mbeltguz@colby.edu",
        "aemoreno@colby.edu",
        "mfreese@colby.edu",
        "obraym25@colby.edu"
    ]

def test_todo_route_post(logged_in_user):
    """Test the '/' route with POST method."""
    test_client, user = logged_in_user

    # Send a POST request
    response = test_client.post('/', data={"task-text": "Task 1"}, follow_redirects=False)

    # Since the route redirects to /home, update the assertion
    assert response.status_code == 302
    assert response.location.endswith(url_for('main.home'))


def test_home_redirects_to_admin(logged_in_admin):
    """Test /home route redirects to admin page for admin users."""
    test_client, admin = logged_in_admin
    
    response = test_client.get('/home', follow_redirects=False)
    
    # Assert that the response redirects to the admin page
    assert response.status_code == 302
    assert response.location.endswith(url_for('main.admin'))


def test_home_redirects_to_task(logged_in_user):
    """Test /home route redirects to task page for non-admin users."""
    test_client, user = logged_in_user
    
    response = test_client.get('/home', follow_redirects=False)
    
    # Assert that the response redirects to the task page
    assert response.status_code == 302
    assert response.location.endswith(url_for('main.task'))




def test_task_route(logged_in_user):
    """Test the /task route for rendering tasks."""
    test_client, user = logged_in_user
    response = test_client.get('/task')
    assert response.status_code == 200
    # Update to check for content actually present in your task.html
    assert b'Task' in response.data
    
    not_found_user = User.query.filter_by(email="notfound@gmail.com").first()
    assert not_found_user is None




def test_subtask_route(logged_in_user):
    test_client, user = logged_in_user
    task = Task.query.first()
    response = test_client.get(f'/subtask/{task.id}')
    assert response.status_code == 200
    # Update to check for content actually present in your subtask.html
    assert b'Subtask' in response.data



def test_steps_route(logged_in_user):
    """Test the /steps route with query params."""
    test_client, _ = logged_in_user
    # Remove nested app context; the test client already provides context
    response = test_client.get('/steps/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'Step 1' in response.data




def test_admin_route(logged_in_admin):
    """Test the /admin route for rendering admin tasks."""
    test_client, admin = logged_in_admin
    response = test_client.get('/admin')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data, f"Response data: {response.data}"



def test_get_students_by_task_route(logged_in_user):
    """Test the /get_students_by_task route for fetching students."""
    test_client, user = logged_in_user
    task = Task.query.first()
    response = test_client.get(f'/get_students_by_task?task={task.title}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'students' in data


def test_get_tasks_by_email_route(logged_in_user):
    """Test the /get_tasks_by_email route."""
    test_client, user = logged_in_user
    response = test_client.get(f'/get_tasks_by_email?email={user.email}')
    assert response.status_code == 200
    data = response.get_json()
    print("THIS IS DATA", data)
    assert 'Content for Task 1' in data['tasks'][0]['content']

def test_admin_view_student_progress_route(logged_in_user):
    """Test the /admin/view_student_progress route."""
    test_client, user = logged_in_user
    task = Task.query.first()
    response = test_client.get(f'/admin/view_student_progress?email={user.email}&task_name={task.title}')
    assert response.status_code == 200
    # Check for specific content in the rendered HTML
    assert b'Subtask 1' in response.data  # Replace with a valid subtask title
    assert b'Complete' in response.data   # Replace with any valid status keyword


def test_get_tags_route(logged_in_user):
    """Test the /get_tags route."""
    test_client, _ = logged_in_user
    response = test_client.get('/get_tags')
    assert response.status_code == 200
    data = response.get_json()
    assert 'tags' in data


def test_get_tags_for_student_route(logged_in_user):
    """Test the /get_tags_for_student route."""
    test_client, _ = logged_in_user
    student = User.query.first()
    response = test_client.get(f'/get_tags_for_student?student={student.name}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'tags' in data


def test_update_tags_tasks_no_data(logged_in_admin):
    """Test /admin/updateTagsTasks with no form data provided."""
    test_client, admin = logged_in_admin

    response = test_client.post(
        '/admin/updateTagsTasks',
        data={},
        follow_redirects=True
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data


def test_update_tags_tasks_valid_tag_assign(logged_in_admin):
    """Test /admin/updateTagsTasks with valid tag assignment."""
    test_client, admin = logged_in_admin

    with test_client.application.app_context():
        user = User(email="test_user@example.com", name="Test User")
        tag = Tag(name="Urgent", html_class="urgent-label")
        db.session.add_all([user, tag])
        db.session.commit()

        # Refresh instances
        db.session.refresh(user)
        db.session.refresh(tag)

    response = test_client.post(
        '/admin/updateTagsTasks',
        data={
            'selectedStudentEmailsInput': user.email,
            'itemName': tag.name,
            'itemType': 'Tag',
            'actionType': 'Assign'
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    with test_client.application.app_context():
        user = User.query.filter_by(email=user.email).first()
        assert tag in user.tags


def test_update_tags_tasks_duplicate_tag_assign(logged_in_admin):
    """Test /admin/updateTagsTasks with duplicate tag assignment."""
    test_client, admin = logged_in_admin

    with test_client.application.app_context():
        user = User(email="test_user@example.com", name="Test User")
        tag = Tag(name="Urgent", html_class="urgent-label")
        user.tags.append(tag)
        db.session.add_all([user, tag])
        db.session.commit()

    response = test_client.post(
        '/admin/updateTagsTasks',
        data={
            'selectedStudentEmailsInput': user.email,
            'itemName': tag.name,
            'itemType': 'Tag',
            'actionType': 'Assign'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True  # Success is returned even if no change happens

    with test_client.application.app_context():
        user = User.query.filter_by(email=user.email).first()
        assert user.tags.count(tag) == 1  # Tag is not duplicated


def test_update_tags_tasks_valid_tag_remove(logged_in_admin):
    """Test /admin/updateTagsTasks with valid tag removal."""
    test_client, admin = logged_in_admin

    with test_client.application.app_context():
        user = User(email="test_user@example.com", name="Test User")
        tag = Tag(name="Urgent", html_class="urgent-label")
        user.tags.append(tag)
        db.session.add_all([user, tag])
        db.session.commit()

    response = test_client.post(
        '/admin/updateTagsTasks',
        data={
            'selectedStudentEmailsInput': user.email,
            'itemName': tag.name,
            'itemType': 'Tag',
            'actionType': 'Remove'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

    with test_client.application.app_context():
        user = User.query.filter_by(email=user.email).first()
        assert tag not in user.tags


def test_update_tags_tasks_invalid_item_type(logged_in_admin):
    """Test /admin/updateTagsTasks with invalid item type."""
    test_client, admin = logged_in_admin

    response = test_client.post(
        '/admin/updateTagsTasks',
        data={
            'selectedStudentEmailsInput': admin.email,
            'itemName': 'SomeItem',
            'itemType': 'InvalidType',
            'actionType': 'Assign'
        },
        follow_redirects=True
    )
    assert response.status_code == 200 
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data


def test_update_tags_tasks_invalid_action_type(logged_in_admin):
    """Test /admin/updateTagsTasks with invalid action type."""
    test_client, admin = logged_in_admin

    response = test_client.post(
        '/admin/updateTagsTasks',
        data={
            'selectedStudentEmailsInput': admin.email,
            'itemName': 'Urgent',
            'itemType': 'Tag',
            'actionType': 'InvalidAction'
        },
        follow_redirects=True
    )
    assert response.status_code == 400  # Assuming a check for invalid action type is implemented
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data



def test_get_tasks_route(logged_in_user):
    """Test the /get_tasks route."""
    test_client, _ = logged_in_user
    response = test_client.get('/get_tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert 'tasks' in data


def test_get_students_by_task_not_found(logged_in_user):
    """Test the /get_students_by_task route with a non-existent task."""
    test_client, _ = logged_in_user
    response = test_client.get('/get_students_by_task?task=NonExistentTask')
    assert response.status_code == 404
    data = response.get_json()
    assert data.get('error') == 'Task not found'


def test_get_tags_for_student_not_found(logged_in_user):
    """Test the /get_tags_for_student route with a non-existent student."""
    test_client, _ = logged_in_user
    response = test_client.get('/get_tags_for_student?student=NonExistentStudent')
    assert response.status_code == 404
    data = response.get_json()
    assert data.get('error') == 'Student not found'


def test_progress_update(logged_in_user):
    """Test the /progress/<int:subtask_id> route for updating progress."""
    test_client, user = logged_in_user

    # Get an existing subtask for the user
    subtask = Subtask.query.first()
    assert subtask is not None, "No subtasks found for testing."

    # Create progress entry if not exists
    progress = Progress.query.filter_by(user_id=user.id, subtask_id=subtask.id).first()
    if not progress:
        progress = Progress(user_id=user.id, subtask_id=subtask.id, task_id=subtask.task_id, complete=False)
        db.session.add(progress)
        db.session.commit()

    # Send GET request to update progress
    response = test_client.get(f'/progress/{subtask.id}', follow_redirects=True)
    assert response.status_code == 200

    # Verify that progress is updated
    updated_progress = Progress.query.filter_by(user_id=user.id, subtask_id=subtask.id).first()
    assert updated_progress.complete is True


def test_get_tasks_by_email_success(logged_in_user):
    """Test /get_tasks_by_email route for valid email."""
    test_client, user = logged_in_user

    # Add a task if none exists
    task = Task.query.first()
    if not task:
        task = Task(title="Sample Task", content="Sample Content")
        db.session.add(task)
        user.tasks.append(task)
        db.session.commit()

    response = test_client.get(f'/get_tasks_by_email?email={user.email}')
    assert response.status_code == 200

    data = response.get_json()
    assert 'tasks' in data
    assert len(data['tasks']) > 0
    assert any(task['title'] == "Task 1" for task in data['tasks'])


def test_get_tasks_by_email_failure(test_client):
    """Test /get_tasks_by_email route with invalid email."""
    
    response = test_client.get('/get_tasks_by_email?email=invalid@example.com')
    assert len(response.get_json()['tasks']) == 0


def test_get_students_by_task_success(logged_in_user):
    test_client, _ = logged_in_user

    with test_client.application.app_context():
        task = Task.query.first()
        # if not task:
        #     task = Task(title="Test Task", content="Test Task Content")
        #     db.session.add(task)
        #     db.session.commit()

        user = User.query.first()
        # if user and task not in user.tasks:
        #     user.tasks.append(task)
        #     db.session.commit()

    response = test_client.get(f'/get_students_by_task?task={task.title}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'students' in data



def test_get_students_by_task_failure(logged_in_user):
    """Test /get_students_by_task route with a non-existent task."""
    test_client, _ = logged_in_user
    response = test_client.get('/get_students_by_task?task=NonExistentTask')
    assert response.status_code == 404

    data = response.get_json()
    assert data.get('error') == 'Task not found'


def test_add_task_to_database_success(logged_in_admin):
    """Test /admin/addTask (POST) for adding a new task."""
    test_client, admin = logged_in_admin

    response = test_client.post(
        '/admin/addTask',
        data={
            'task_name': 'New Test Task',
            'deadline': '2024-12-31',
            'subtask_title[]': ['Subtask 1', 'Subtask 2'],
            'step_title[0]': 'Step 1',
            'step_title[1]': 'Step 2',
            'step_content[0]': 'Step 1 Content',
            'step_content[1]': 'Step 2 Content',
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    # Verify the task exists in the database
    task = Task.query.filter_by(title='New Test Task').first()
    assert task is not None
    assert len(task.subtasks) == 2



def test_get_tags_success(logged_in_user):
    """Test /get_tags route for fetching all tags."""
    test_client, _ = logged_in_user

    # Ensure there is at least one tag in the database
    if not Tag.query.first():
        db.session.add(Tag(name="Test Tag", html_class="test-class"))
        db.session.commit()

    response = test_client.get('/get_tags')
    assert response.status_code == 200

    data = response.get_json()
    assert 'tags' in data
    assert len(data['tags']) > 0
    assert any(tag['name'] == "Urgent" for tag in data['tags'])


def test_get_students_by_task_no_students(logged_in_user):
    """Test /get_students_by_task when no students are assigned."""
    test_client, _ = logged_in_user

    with test_client.application.app_context():
        task = Task(title="Empty Task", content="No students")
        db.session.add(task)
        db.session.commit()

        # Clear students
        task.students = []
        db.session.commit()

    response = test_client.get(f'/get_students_by_task?task={task.title}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'students' in data
    assert len(data['students']) == 0


def test_get_tags_for_student_invalid_input(logged_in_user):
    """Test /get_tags_for_student with invalid input."""
    test_client, _ = logged_in_user

    # Send a request with no student name
    response = test_client.get('/get_tags_for_student?student=')
    assert response.status_code == 404

    data = response.get_json()
    assert data.get('error') == 'Student not found'


def test_task_page_rendered_data(logged_in_user):
    """Test if /task page renders correct data."""
    test_client, user = logged_in_user

    # Create a task and assign to the user
    task = Task(title="Rendered Task", content="Task for rendering")
    user.tasks.append(task)
    db.session.commit()

    response = test_client.get('/task')
    assert response.status_code == 200
    assert b"Rendered Task" in response.data

def test_add_label_success(logged_in_admin):
    """Test /add_label route for successfully adding a label."""
    test_client, admin = logged_in_admin

    response = test_client.post(
        '/add_label',
        json={
            'labelName': 'Urgent',
            'labelColor': 'bg-danger',
        },
        headers={'Content-Type': 'application/json'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Label added successfully'
    assert data['label']['name'] == 'Urgent'



def test_add_label_duplicate(logged_in_user):
    """Test /add_label route for handling duplicate labels."""
    test_client, user = logged_in_user

    # Only allow admin users to perform this action
    if user.email not in admin_emails:
        pytest.skip("Non-admin user cannot access this route.")

    # Add the same label twice
    test_client.post('/add_label', json={'labelName': 'Duplicate', 'labelColor': 'bg-warning'})
    response = test_client.post('/add_label', json={'labelName': 'Duplicate', 'labelColor': 'bg-warning'})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Label already exists'

def test_add_label_invalid_input(logged_in_admin):
    """Test /add_label route for invalid input."""
    test_client, admin = logged_in_admin

    # Case 1: Missing label_name
    response = test_client.post(
        '/add_label',
        json={
            'labelColor': 'bg-danger'  # Missing 'labelName'
        },
        follow_redirects=True,
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data.get('error') == 'Invalid input'

    # Case 2: Missing label_color
    response = test_client.post(
        '/add_label',
        json={
            'labelName': 'Urgent'  # Missing 'labelColor'
        },
        follow_redirects=True,
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data.get('error') == 'Invalid input'

    # Case 3: Both missing
    response = test_client.post(
        '/add_label',
        json={},  # No data
        follow_redirects=True,
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data.get('error') == 'Invalid input'


def test_admin_view_student_progress_no_student(logged_in_admin):
    """Test /admin/view_student_progress with a non-existent student."""
    test_client, admin = logged_in_admin

    response = test_client.get('/admin/view_student_progress?email=nonexistent@example.com&task_name=Test Task')
    assert response.status_code == 404
    assert b"Student not found" in response.data



def test_admin_view_student_progress_no_task(logged_in_user):
    """Test /admin/view_student_progress with a non-existent task."""
    test_client, user = logged_in_user

    # Only allow admin users to perform this action
    if user.email not in admin_emails:
        pytest.skip("Non-admin user cannot access this route.")

    response = test_client.get(f'/admin/view_student_progress?email={user.email}&task_name=NonExistentTask')
    assert response.status_code == 404
    assert b"Task not found" in response.data


def test_add_task_to_database_invalid_data(logged_in_user):
    """Test /admin/addTask route with invalid input data."""
    test_client, user = logged_in_user

    # Only allow admin users to perform this action
    if user.email not in admin_emails:
        pytest.skip("Non-admin user cannot access this route.")

    response = test_client.post(
        '/admin/addTask',
        data={
            'task_name': '',  # Missing task name
            'deadline': '',
            'subtask_title[]': [],
        },
        follow_redirects=True,
    )
    assert response.status_code == 400


def test_get_tasks_no_tasks(logged_in_user):
    """Test /get_tasks when no tasks are present in the database."""
    test_client, _ = logged_in_user

    # Remove all tasks from the database
    with test_client.application.app_context():
        Task.query.delete()
        db.session.commit()

    response = test_client.get('/get_tasks')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Task not found'


def test_add_task_to_database_with_steps(logged_in_admin):
    """Test adding a task with subtasks and steps to the database."""
    test_client, admin = logged_in_admin

    # Prepare form data for the POST request
    task_data = {
        'task_name': 'Test Task with Steps',
        'deadline': '2024-12-31',
        'subtask_title[]': ['Subtask 1', 'Subtask 2'],
        'step_title[0]': 'Step 1 for Subtask 1',
        'step_content[0]': 'Content for Step 1 of Subtask 1',
        'step_title[1]': 'Step 1 for Subtask 2',
        'step_content[1]': 'Content for Step 1 of Subtask 2',
    }

    response = test_client.post('/admin/addTask', data=task_data, follow_redirects=True)
    assert response.status_code == 200

    # Verify the task was added to the database
    with test_client.application.app_context():
        task = Task.query.filter_by(title='Test Task with Steps').first()
        assert task is not None
        assert len(task.subtasks) == 2

        # Verify the first subtask and its steps
        subtask1 = Subtask.query.filter_by(title='Subtask 1').first()
        assert subtask1 is not None
        assert len(subtask1.steps) == 1
        step1 = subtask1.steps[0]
        assert step1.title == 'Step 1 for Subtask 1'
        assert step1.content == 'Content for Step 1 of Subtask 1'

        # Verify the second subtask and its steps
        subtask2 = Subtask.query.filter_by(title='Subtask 2').first()
        assert subtask2 is not None
        assert len(subtask2.steps) == 1
        step2 = subtask2.steps[0]
        assert step2.title == 'Step 1 for Subtask 2'
        assert step2.content == 'Content for Step 1 of Subtask 2'
