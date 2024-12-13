# Pylint outer name doesn't understand context of test_client
# pylint: disable=redefined-outer-name
'''Imports the necessary modules for testing.'''
from datetime import datetime
import pytest
from website import create_app, db
from website.models import User, Task, Subtask, Step, Progress, Tag

@pytest.fixture(scope="module")
def test_client():
    """Set up a Flask test client."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture(scope="function")
def init_database(test_client):
    """Initialize the database with test data."""
    with test_client.application.app_context():

        # Clear existing data
        db.session.query(Progress).delete()
        db.session.query(Step).delete()
        db.session.query(Subtask).delete()
        db.session.query(Task).delete()
        db.session.query(Tag).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Add test users
        user1 = User(email="test_user1@example.com", name="Test User 1")
        user2 = User(email="test_user2@example.com", name="Test User 2")
        admin_user = User(email="mbeltguz@colby.edu", name="Admin User")  # New admin user

        db.session.add_all([user1, user2, admin_user])
        db.session.commit()

        # Add tasks
        task1 = Task(title="Task 1", content="Content for Task 1", deadline=datetime.utcnow())
        task2 = Task(title="Task 2", content="Content for Task 2", deadline=datetime.utcnow())
        db.session.add_all([task1, task2])
        db.session.commit()

        # Associate users with tasks
        users = [user1, user2]
        tasks = [task1, task2]
        for task in tasks:
            existing_users_in_task = set(user.id for user in task.users)
            users_to_add = [user for user in users if user.id not in existing_users_in_task]
            for user in users_to_add:
                task.users.append(user)
        db.session.commit()

        # Add subtasks
        subtasks_task1 = [
            Subtask(title="Subtask 1.1", content="Content for Subtask 1.1", task_id=task1.id),
            Subtask(title="Subtask 1.2", content="Content for Subtask 1.2", task_id=task1.id),
            Subtask(title="Subtask 1.3", content="Content for Subtask 1.3", task_id=task1.id),
        ]
        subtasks_task2 = [
            Subtask(title="Subtask 2.1", content="Content for Subtask 2.1", task_id=task2.id),
            Subtask(title="Subtask 2.2", content="Content for Subtask 2.2", task_id=task2.id),
        ]
        db.session.add_all(subtasks_task1 + subtasks_task2)
        db.session.commit()

        # Add steps
        steps = [
            Step(title="Step 1.1.1", content="Content for Step 1.1.1",
                 progress=0, subtask_id=subtasks_task1[0].id),
            Step(title="Step 1.1.2", content="Content for Step 1.1.2",
                 progress=50, subtask_id=subtasks_task1[0].id),
            Step(title="Step 1.2.1", content="Content for Step 1.2.1",
                 progress=25, subtask_id=subtasks_task1[1].id),
            Step(title="Step 1.3.1", content="Content for Step 1.3.1",
                 progress=75, subtask_id=subtasks_task1[2].id),
            Step(title="Step 2.1.1", content="Content for Step 2.1.1",
                 progress=30, subtask_id=subtasks_task2[0].id),
            Step(title="Step 2.2.1", content="Content for Step 2.2.1",
                 progress=60, subtask_id=subtasks_task2[1].id),
        ]
        db.session.add_all(steps)
        db.session.commit()

        # Add progress records
        progress_records = [
            Progress(complete=False, user_id=user1.id, task_id=task1.id,
                     subtask_id=subtasks_task1[0].id),
            Progress(complete=True, user_id=user1.id, task_id=task1.id,
                     subtask_id=subtasks_task1[1].id),
            Progress(complete=False, user_id=user1.id, task_id=task2.id,
                     subtask_id=subtasks_task2[0].id),
            Progress(complete=True, user_id=user2.id, task_id=task2.id,
                     subtask_id=subtasks_task2[1].id),
        ]
        db.session.add_all(progress_records)
        db.session.commit()

        # Add tags
        tag1 = Tag(name="Urgent", html_class="label-urgent")
        tag2 = Tag(name="Optional", html_class="label-optional")
        db.session.add_all([tag1, tag2])
        user1.tags.append(tag1)
        user2.tags.append(tag2)

        db.session.commit()

    yield db

    with test_client.application.app_context():
        db.session.rollback()



@pytest.fixture(scope="function")
def logged_in_user(test_client, init_database):
    """Log in a test user and ensure request context."""
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        assert user is not None

    with test_client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

    yield test_client, user


@pytest.fixture(scope="function")
def logged_in_admin(test_client, init_database):
    """Log in as an admin user."""
    with test_client.application.app_context():
        # Ensure the admin user exists
        admin = User.query.filter_by(email="mbeltguz@colby.edu").first()
        assert admin is not None, "Admin user not found in the database"

    # Set the session to simulate an admin login
    with test_client.session_transaction() as sess:
        sess["_user_id"] = str(admin.id)
        sess["_fresh"] = True

    yield test_client, admin
