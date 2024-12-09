from website.models import User, Task, Subtask, Step, Progress, Tag

def test_create_user(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a user is queried by email
    THEN ensure the correct user is returned
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user@example.com").first()
        assert user is not None
        assert user.name == "Test User"

def test_task_user_relationship(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a task is assigned to a user
    THEN ensure the user is associated with the task
    """
    with test_client.application.app_context():

        user = User.query.filter_by(email="test_user@example.com").first()
        task = Task.query.filter_by(title="Test Task").first()

        user.tasks.append(task)

        assert task in user.tasks
        assert user in task.users


def test_create_subtask(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a subtask is queried by title
    THEN ensure the correct subtask is returned
    """
    with test_client.application.app_context():
        subtask = Subtask.query.filter_by(title="Test Subtask").first()
        assert subtask is not None
        assert subtask.content == "Subtask Content"


def test_task_subtask_relationship(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a subtask is linked to a task
    THEN ensure the task has the correct subtask
    """
    with test_client.application.app_context():
        task = Task.query.filter_by(title="Test Task").first()
        subtask = Subtask.query.filter_by(task_id=task.id).first()
        assert subtask in task.subtasks


def test_create_step(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a step is queried by title
    THEN ensure the correct step is returned
    """
    with test_client.application.app_context():
        step = Step.query.filter_by(title="Test Step").first()
        assert step is not None
        assert step.content == "Step Content"


def test_subtask_step_relationship(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a step is linked to a subtask
    THEN ensure the subtask has the correct step
    """
    with test_client.application.app_context():
        subtask = Subtask.query.filter_by(title="Test Subtask").first()
        step = Step.query.filter_by(subtask_id=subtask.id).first()
        assert step in subtask.steps


def test_progress_creation(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN progress is queried
    THEN ensure the correct progress record is returned
    """
    with test_client.application.app_context():
        progress = Progress.query.first()
        assert progress is not None
        assert not progress.complete


def test_user_progress_relationship(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN progress is linked to a user
    THEN ensure the user has the correct progress record
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user@example.com").first()
        progress = Progress.query.filter_by(user_id=user.id).first()
        assert progress in user.progress


def test_create_tag(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a tag is queried by name
    THEN ensure the correct tag is returned
    """
    with test_client.application.app_context():
        tag = Tag.query.filter_by(name="Co'26").first()
        assert tag is not None
        assert tag.html_class == "label-Co'26"


def test_user_tag_relationship(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a tag is assigned to a user
    THEN ensure the user is associated with the tag
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user@example.com").first()
        tag = Tag.query.filter_by(name="Co'26").first()
        assert tag in user.tags
        assert user in tag.users

def test_update_user_task(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a task assigned to a user is updated
    THEN ensure the changes are reflected in the user's tasks
    """
    with test_client.application.app_context():

        user = User.query.filter_by(email="test_user@example.com").first()
        task = Task.query.filter_by(title="Test Task").first()

        user.tasks.append(task)
        task.title = "Updated Task Title"

        assert task.title == "Updated Task Title"
        assert task in user.tasks


def test_remove_user_task(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a task is removed from a user
    THEN ensure the user no longer has the task
    """
    with test_client.application.app_context():

        user = User.query.filter_by(email="test_user@example.com").first()
        task = Task.query.filter_by(title="Test Task").first()

        user.tasks.append(task)
        user.tasks.remove(task)

        assert task not in user.tasks


def test_assign_multiple_tags_to_user(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN multiple tags are assigned to a user
    THEN ensure the user is associated with all tags
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user@example.com").first()

        tag1 = Tag(name="Urgent", html_class="label-urgent")
        tag2 = Tag(name="Optional", html_class="label-optional")
        user.tags.extend([tag1, tag2])

        assert tag1 in user.tags
        assert tag2 in user.tags


def test_progress_task_completion(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a task's progress is marked complete
    THEN ensure the progress reflects the completion
    """
    with test_client.application.app_context():
        progress = Progress.query.first()
        progress.complete = True

        assert progress.complete is True


def test_step_belongs_to_correct_subtask(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN querying a step
    THEN ensure it belongs to the correct subtask
    """
    with test_client.application.app_context():
        step = Step.query.filter_by(title="Test Step").first()
        subtask = Subtask.query.filter_by(id=step.subtask_id).first()

        assert step in subtask.steps


def test_subtask_without_steps(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a subtask without steps is queried
    THEN ensure it has no steps
    """
    with test_client.application.app_context():
        subtask = Subtask.query.filter_by(title="Test Subtask").first()
        subtask.steps.clear()

        assert len(subtask.steps) == 0

