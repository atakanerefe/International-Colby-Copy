# Pylint does not understand init_database function in conftest.py
# pylint: disable=unused-argument
''' Imports the necessary modules for testing models. '''
from website.models import User, Task, Subtask, Step, Progress, Tag

def test_create_user(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a user is queried by email
    THEN ensure the correct user is returned
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        assert user is not None
        assert user.name == "Test User 1"

def test_task_user_relationship(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN a task is assigned to a user
    THEN ensure the user is associated with the task
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        task = Task.query.filter_by(title="Task 1").first()

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
        subtask = Subtask.query.filter_by(title="Subtask 1.1").first()
        assert subtask is not None
        assert subtask.content == "Content for Subtask 1.1"

def test_task_subtask_relationship(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a subtask is linked to a task
    THEN ensure the task has the correct subtask
    """
    with test_client.application.app_context():
        task = Task.query.filter_by(title="Task 1").first()
        subtask = Subtask.query.filter_by(task_id=task.id).first()
        assert subtask in task.subtasks

def test_create_step(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a step is queried by title
    THEN ensure the correct step is returned
    """
    with test_client.application.app_context():
        step = Step.query.filter_by(title="Step 1.1.1").first()
        assert step is not None
        assert step.content == "Content for Step 1.1.1"

def test_subtask_step_relationship(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a step is linked to a subtask
    THEN ensure the subtask has the correct step
    """
    with test_client.application.app_context():
        subtask = Subtask.query.filter_by(title="Subtask 1.1").first()
        step = Step.query.filter_by(subtask_id=subtask.id).first()
        assert step in subtask.steps

def test_progress_creation(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN progress is queried
    THEN ensure the correct progress record is returned
    """
    with test_client.application.app_context():
        progress = Progress.query.filter_by(complete=False).first()
        assert progress is not None
        assert not progress.complete

def test_user_progress_relationship(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN progress is linked to a user
    THEN ensure the user has the correct progress record
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        progress = Progress.query.filter_by(user_id=user.id).first()
        assert progress in user.progress

def test_create_tag(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a tag is queried by name
    THEN ensure the correct tag is returned
    """
    with test_client.application.app_context():
        tag = Tag.query.filter_by(name="Urgent").first()
        assert tag is not None
        assert tag.html_class == "label-urgent"

def test_user_tag_relationship(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a tag is assigned to a user
    THEN ensure the user is associated with the tag
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        tag = Tag.query.filter_by(name="Urgent").first()
        assert tag in user.tags
        assert user in tag.users

def test_update_user_task(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a task assigned to a user is updated
    THEN ensure the changes are reflected in the user's tasks
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        task = Task.query.filter_by(title="Task 1").first()

        user.tasks.append(task)
        task.title = "Updated Task Title"

        assert task.title == "Updated Task Title"
        assert task in user.tasks

def test_remove_user_task(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a task is removed from a user
    THEN ensure the user no longer has the task
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        task = Task.query.filter_by(title="Task 11").first()

        user.tasks.append(task)
        user.tasks.remove(task)

        assert task not in user.tasks

def test_assign_multiple_tags_to_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN multiple tags are assigned to a user
    THEN ensure the user is associated with all tags
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        tag1 = Tag.query.filter_by(name="Urgent").first()
        tag2 = Tag.query.filter_by(name="Optional").first()

        user.tags.extend([tag1, tag2])

        assert tag1 in user.tags
        assert tag2 in user.tags


def test_progress_task_completion(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a task's progress is marked complete
    THEN ensure the progress reflects the completion
    """
    with test_client.application.app_context():
        progress = Progress.query.filter_by(complete=False).first()
        progress.complete = True

        assert progress.complete is True

def test_step_belongs_to_correct_subtask(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN querying a step
    THEN ensure it belongs to the correct subtask
    """
    with test_client.application.app_context():
        step = Step.query.filter_by(title="Step 1.1.1").first()
        subtask = Subtask.query.filter_by(id=step.subtask_id).first()

        assert step in subtask.steps

def test_subtask_without_steps(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a subtask without steps is queried
    THEN ensure it has no steps
    """
    with test_client.application.app_context():
        subtask = Subtask.query.filter_by(title="Subtask 1.1").first()
        subtask.steps.clear()

        assert len(subtask.steps) == 0

def test_multiple_tasks_per_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN multiple tasks are assigned to a single user
    THEN ensure the user is associated with all assigned tasks
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        task1 = Task.query.filter_by(title="Task 1").first()
        task2 = Task.query.filter_by(title="Task 2").first()

        user.tasks.extend([task1, task2])

        assert task1 in user.tasks
        assert task2 in user.tasks
        assert user in task1.users
        assert user in task2.users

def test_remove_task_with_subtasks(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a task with subtasks is removed
    THEN ensure the task and its subtasks are no longer in the database
    """
    with test_client.application.app_context():
        task = Task.query.filter_by(title="Task 1").first()
        Subtask.query.filter_by(task_id=task.id).delete()
        Task.query.filter_by(id=task.id).delete()

        assert Task.query.filter_by(title="Task 1").first() is None
        assert Subtask.query.filter_by(task_id=task.id).count() == 0

def test_step_progress_accumulation(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN all steps under a subtask are completed
    THEN ensure the total progress of the subtask reflects the completion
    """
    with test_client.application.app_context():
        subtask = Subtask.query.filter_by(title="Subtask 1.1").first()
        steps = Step.query.filter_by(subtask_id=subtask.id).all()

        for step in steps:
            step.progress = 100  # Mark all steps complete

        total_progress = sum(step.progress for step in steps) / len(steps)
        assert total_progress == 100

def test_progress_status_across_tasks(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN querying progress records for a user
    THEN ensure the correct completion status is returned for all tasks
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="test_user1@example.com").first()
        progress_records = Progress.query.filter_by(user_id=user.id).all()

        completed = [progress for progress in progress_records if progress.complete]
        not_completed = [progress for progress in progress_records if not progress.complete]

        assert len(completed) > 0
        assert len(not_completed) > 0


def test_task_without_subtasks_no_db():
    """
    GIVEN a Task object
    WHEN it is created without any subtasks
    THEN ensure it has no subtasks
    """
    # Create a standalone task object
    task = Task(title="Standalone Task", content="This task has no subtasks.")

    # Assert that the task has no subtasks
    assert len(task.subtasks) == 0
