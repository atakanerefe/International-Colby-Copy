import pytest
from website import create_app, db
from website.models import User, Task, Subtask, Step, Progress, Tag
from datetime import datetime


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

        db.session.query(Progress).delete()
        db.session.query(Step).delete()
        db.session.query(Subtask).delete()
        db.session.query(Task).delete()
        db.session.query(Tag).delete()
        db.session.query(User).delete()
        db.session.commit()

        user = User(email="test_user@example.com", name="Test User")
        db.session.add(user)
        db.session.commit()

        task = Task(title="Test Task", content="This is a test task.", deadline=datetime.utcnow())
        db.session.add(task)
        db.session.commit()

        subtask = Subtask(title="Test Subtask", content="Subtask Content", task_id=task.id)
        db.session.add(subtask)
        db.session.commit()

        step = Step(title="Test Step", content="Step Content", progress=0, subtask_id=subtask.id)
        db.session.add(step)

        progress = Progress(complete=False, user_id=user.id, task_id=task.id, subtask_id=subtask.id)
        db.session.add(progress)

        tag = Tag(name="Co'26", html_class="label-Co'26")
        db.session.add(tag)
        user.tags.append(tag)

        db.session.commit()

    yield db

    with test_client.application.app_context():
        db.session.rollback()





