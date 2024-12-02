from website.models import User, Task, Subtask, Step, Progress, Tag

def test_user_one_task():
    user = User(email="student1@example.com")
    task = Task(title="Task 1", content="Content 1")
    user.tasks.append(task)
    assert user.tasks[0].title == "Task 1"
    assert user.tasks[0].content == "Content 1"

def test_user_multiple_tasks():
    user = User(email="student1@example.com")
    task1 = Task(title="Task 1", content="Content 1")
    task2 = Task(title="Task 2", content="Content 2")
    user.tasks.append(task1)
    user.tasks.append(task2)
    assert user.tasks[0].title == "Task 1"
    assert user.tasks[0].content == "Content 1"
    assert user.tasks[1].title == "Task 2"
    assert user.tasks[1].content == "Content 2"

def test_user_one_tag():
    user = User(email="student1@example.com")
    tag = Tag(name="Tag 1", html_class="tag1")
    user.tags.append(tag)
    assert user.tags[0].name == "Tag 1"
    assert user.tags[0].html_class == "tag1"

def test_user_multiple_tags():
    user = User(email="student1@example.com")
    tag1 = Tag(name="Tag 1", html_class="tag1")
    tag2 = Tag(name="Tag 2", html_class="tag2")
    user.tags.append(tag1)
    user.tags.append(tag2)
    assert user.tags[0].name == "Tag 1"
    assert user.tags[0].html_class == "tag1"

def test_user_progress():
    user = User(email="student1@example.com")
    task = Task(title="Task 1", content="Task Content 1")
    subtask = Subtask(title="Subtask 1", content="Subtask Content 1", task=task)
    step = Step(title="Step 1", content="Step Content 1", progress=0, subtask=subtask)
    progress = Progress(complete=False, task=task, subtask=subtask, user=user)
    
    user.progress.append(progress)
    assert user.progress[0].complete == False
    assert user.progress[0].task.title == "Task 1"
    assert user.progress[0].subtask.title == "Subtask 1"
    assert user.progress[0].user_id == user.id