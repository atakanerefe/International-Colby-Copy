from flask import Blueprint, jsonify, render_template, redirect, url_for
from flask import request
from website import db
from .models import Progress, Subtask, User, Task, Step, user_task_association_table
from flask_login import login_required, current_user
from datetime import datetime

# Create a blueprint
main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'POST':
        task = request.form['task-text']
        new_task = Task(text=task, status='not-completed', user=current_user)
        db.session.add(new_task)
        db.session.commit()
        
    tasks = Task.query.filter_by(user=current_user).all()
    return render_template('task.html', tasks=tasks)

@main_blueprint.route('/task')
@login_required
def task():
    tasks = run_get_tasks_by_email(current_user.email)
    return render_template('task.html', tasks=tasks)

@main_blueprint.route('/subtask')
@login_required
def subtask():
    return render_template('subtask.html')

@main_blueprint.route('/steps')
@login_required
def steps():
    step = request.args.get('step', default=1, type=int)
    return render_template('steps.html', active_step=step)

@main_blueprint.route('/admin')
@login_required
def admin():

    # DYNAMICALLY DISPLAY TASKS FOR FUTURE USE
    return render_template('allStudents.html', tasks=Task.query.all())
    # return render_template('allStudents.html')

@main_blueprint.route('/admin/addTask')
@login_required
def addTask():
    return render_template('addTask.html')

@main_blueprint.route('/get_students_by_task')
def get_students_by_task():
    task_name = request.args.get('task')

    # Fetch the task by its title
    task = Task.query.filter_by(title=task_name).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # Fetch all users assigned to this task using the user_task_association_table
    students = User.query.join(user_task_association_table).join(Task).filter(Task.id == task.id).all()

    students_data = []

    for student in students:
        # Get all subtasks for this task
        subtasks = Subtask.query.filter_by(task_id=task.id).all()

        total_subtasks = len(subtasks)
        completed_subtasks = 0

        # Calculate progress for each student on the subtasks
        for subtask in subtasks:
            # Fetch the progress for the student and subtask
            progress = Progress.query.filter_by(user_id=student.id, subtask_id=subtask.id).first()
            if progress and progress.complete:
                completed_subtasks += 1

        # Calculate the progress percentage
        progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

        students_data.append({
            'email': student.email,
            'name' : student.name,
            'progress': {
                'completed': completed_subtasks,
                'total': total_subtasks,
                'percent': progress_percent
            }
        })

    return jsonify({'students': students_data})

@main_blueprint.route('/get_tasks_by_email')
def get_tasks_by_email():

    email = request.args.get('email')
    return jsonify({'tasks': run_get_tasks_by_email(email, js_call=True)})

def run_get_tasks_by_email(email, js_call=False):
   # get user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # get progress intances for the user
    progress = Progress.query.filter_by(user_id=user.id).all()

    # get all unique tasks from task_id column in progress
    task_ids = set(progress_entry.task_id for progress_entry in progress)

    tasks_data = []

    for task_id in task_ids:
        
        # get all subtasks in progress that have task_id
        subtasks = [progress_entry for progress_entry in progress if progress_entry.task_id == task_id]
        
        # get number of subtasks that are complete from subtasks
        completed_subtasks = sum(1 for subtask in subtasks if subtask.complete)

        # calculate progress as a percentage
        progress_percent = (completed_subtasks / len(subtasks)) * 100 if len(subtasks) > 0 else 0

        task = Task.query.filter_by(id=task_id).first()

        tasks_data.append({
            'title': task.title,
            'content': task.content,
            'progress': {
                'completed': completed_subtasks,
                'total': len(subtasks),
                'percent': progress_percent
            }
        })
    return tasks_data


@main_blueprint.route('/admin/view_student_progress')
@login_required
def adminViewStudentProgress():
    student_email = request.args.get('email')
    task_name = request.args.get('task_name')

    # Fetch the student and the task by name
    student = User.query.filter_by(email=student_email).first()
    if not student:
        return "Student not found", 404

    task = Task.query.filter_by(title=task_name).first()
    if not task:
        return "Task not found", 404

    # Fetch all subtasks for the task
    subtasks = Subtask.query.filter_by(task_id=task.id).all()

    # Fetch progress for the student
    progress_data = Progress.query.filter_by(user_id=student.id, task_id=task.id).all()

    # Create a dictionary of progress for fast lookup
    progress_dict = {progress.subtask_id: progress.complete for progress in progress_data}

    subtasks_progress = []
    for subtask in subtasks:
        status = 'complete' if progress_dict.get(subtask.id, False) else 'incomplete'
        subtasks_progress.append({
            'subtask': subtask.title,
            'description': subtask.content,  # Add description here
            'status': status
        })

    # Calculate overall progress
    completed_subtasks = sum(1 for subtask in subtasks_progress if subtask['status'] == 'complete')
    total_subtasks = len(subtasks)
    progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

    progress_ratio = f"{completed_subtasks} / {total_subtasks}"  # Show progress as a ratio, e.g., "2 / 5"
    
    return render_template('adminViewStudentProgress.html', student=student, task=task, 
                           subtasks=subtasks_progress, progress_percent=progress_percent, progress_ratio=progress_ratio)

@main_blueprint.route('/admin/addTask', methods=['POST'])
@login_required
def addTaskToDatabase():
    # Get form data
    task_name = request.form.get('task_name')
    deadline_str = request.form.get('deadline')
    subtask_titles = request.form.getlist('subtask_title[]')
    step_titles = []
    for key, value in request.form.items():
        if key.startswith('step_title['):
            subtask_index = int(key.split('[')[1].split(']')[0])
            while len(step_titles) <= subtask_index:
                step_titles.append([])
            step_titles[subtask_index].append(value)

    # Convert deadline to datetime
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None

    # Create the task
    task = Task(title=task_name, content=f"Task created by {current_user.name}", deadline=deadline)
    db.session.add(task)
    db.session.commit()

    # Create subtasks and steps
    for i, subtask_title in enumerate(subtask_titles):
        subtask = Subtask(title=subtask_title, content=f"Subtask for {task_name}", task_id=task.id)
        db.session.add(subtask)
        db.session.commit()

        if i < len(step_titles):
            for step_title in step_titles[i]:
                step = Step(title=step_title, content=f"Step for {subtask_title}", subtask_id=subtask.id, progress=0)
                db.session.add(step)
        db.session.commit()

    # Assign task to all users (optional)
    users = User.query.all()
    for user in users:
        task.users.append(user)
        for subtask in task.subtasks:
            progress = Progress(user_id=user.id, subtask_id=subtask.id, task_id=task.id, complete=False)
            db.session.add(progress)
    db.session.commit()

    return redirect(url_for('main.admin'))

def add_sample_data():
    # Create or fetch users
    users_data = [
        "obraym25@colby.edu",
        "ybmold25@colby.edu",
        "pyang25@colby.edu",
        "aerefe26@colby.edu"
    ]

    users_name = [
        "Owen",
        "Yela",
        "Tricia",
        "Atakan"
    ]
    # Add users if they don't already exist in the database
    users = []
    for email, name in zip(users_data, users_name):
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email=email, name=name)
            db.session.add(new_user)
            users.append(new_user)
        else:
            users.append(existing_user)
    db.session.commit()

    # Fetch the users dynamically
    user_ids = [user.id for user in users]

    # Create a task (this task can be assigned to multiple users)
    task = Task.query.filter_by(title="First Year Check In").first()
    if not task:
        task = Task(title="First Year Check In", content="This is a sample task.")
        db.session.add(task)
        db.session.commit()

    # Check if the user-task association already exists before adding
    existing_users_in_task = set(user.id for user in task.users)  # Set of user IDs already associated with this task
    users_to_add = [user for user in users if user.id not in existing_users_in_task]

    if users_to_add:
        # Add users who are not yet associated with the task
        for user in users_to_add:
            task.users.append(user)
        db.session.commit()

    # Create subtasks and assign them to the task
    subtasks_data = [
        {"title": "I-20 Signature", "content": "Go to Aura Moreno's office in Cotter Union 239 to get your I-20 signed."},
        {"title": "Get US Phone Number", "content": "Pick up a SIM card from the Pugh Center or use a free Google Voice number."},
        {"title": "Bla Bla Bla 1", "content": "Bla Bla Bla 1"},
        {"title": "Bla Bla Bla 2", "content": "Bla Bla Bla 2"},
        {"title": "Bla Bla Bla 3", "content": "Bla Bla Bla 3"},
    ]

    subtasks = []
    for subtask_data in subtasks_data:
        subtask = Subtask.query.filter_by(title=subtask_data["title"], task_id=task.id).first()
        if not subtask:
            subtask = Subtask(title=subtask_data["title"], content=subtask_data["content"], task_id=task.id)
            db.session.add(subtask)
            subtasks.append(subtask)
    db.session.commit()

    # Track progress for each user on the same task
    progress_data = [
        {"user": users[0], "subtasks_completed": [1, 2, 3]},  # User 1 has completed subtasks 1, 2, 3
        {"user": users[1], "subtasks_completed": [2, 4]},     # User 2 has completed subtasks 2, 4
        {"user": users[2], "subtasks_completed": [3, 5]},     # User 3 has completed subtasks 3, 5
        {"user": users[3], "subtasks_completed": [1, 4, 5]}    # User 4 has completed subtasks 1, 4, 5
    ]

    # For each user, create progress records for their respective subtasks
    for progress_entry in progress_data:
        user = progress_entry["user"]
        for i, subtask in enumerate(subtasks):
            progress = Progress.query.filter_by(user_id=user.id, subtask_id=subtask.id).first()
            if not progress:
                complete = True if (i + 1) in progress_entry["subtasks_completed"] else False
                progress = Progress(complete=complete, user_id=user.id, subtask_id=subtask.id, task_id=task.id)
                db.session.add(progress)
    db.session.commit()