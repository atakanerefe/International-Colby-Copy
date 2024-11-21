from flask import Blueprint, jsonify, render_template, redirect, url_for
from flask import request
from website import db
from .models import Progress, Subtask, User, Task, user_task_association_table
from flask_login import login_required, current_user

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
    return render_template('todo.html', tasks=tasks)

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
    return render_template('admin_home.html')

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