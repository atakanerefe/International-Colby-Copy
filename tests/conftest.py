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
def init_database(testing_client):
    """Initialize the database with test data."""
    with testing_client.application.app_context():

        db.session.query(Progress).delete()
        db.session.query(Step).delete()
        db.session.query(Subtask).delete()
        db.session.query(Task).delete()
        db.session.query(Tag).delete()
        db.session.query(User).delete()
        db.session.commit()

        user1 = User(email="test_user1@example.com", name="Test User 1")
        user2 = User(email="test_user2@example.com", name="Test User 2")
        db.session.add_all([user1, user2])
        db.session.commit()

        task1 = Task(title="Task 1", content="Content for Task 1", deadline=datetime.utcnow())
        task2 = Task(title="Task 2", content="Content for Task 2", deadline=datetime.utcnow())
        db.session.add_all([task1, task2])
        db.session.commit()

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

        tag1 = Tag(name="Urgent", html_class="label-urgent")
        tag2 = Tag(name="Optional", html_class="label-optional")
        db.session.add_all([tag1, tag2])
        user1.tags.append(tag1)
        user2.tags.append(tag2)

        db.session.commit()

    yield db

    with test_client.application.app_context():
        db.session.rollback()
