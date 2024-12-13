# Pytest too many arguments only for sample data entry
# pytest: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
'''Uses flask to manage user access and flow. 
Gets database classes from models and databse from website.'''
from datetime import datetime
from flask import Blueprint, jsonify, render_template, redirect, url_for
from flask import request
from flask_login import login_required, current_user
from website import db
from .models import Progress, Subtask, User, Task, Step, Tag
from .models import user_task_association_table, user_tag_association_table

# Create a blueprint
main_blueprint = Blueprint('main', __name__)

admin_emails = [
        "mbeltguz@colby.edu",
        "aemoreno@colby.edu",
        "mfreese@colby.edu",
        "obraym25@colby.edu"
    ]

def get_subtask_status_by_progress(cur_subtask):
    '''Get the status of a subtask based on the progress of the user.'''
    cur_progress = Progress.query.filter_by(user_id=current_user.id,
                                            subtask_id=cur_subtask.id).first()
    if cur_progress:
        return 'complete' if cur_progress.complete else 'incomplete'
    return 'incomplete'

@main_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def startup():
    '''Redirect to the home page upon entering basic site url.'''
    return redirect(url_for('main.home'))

@main_blueprint.route('/home')
@login_required
def home():
    '''Redirects to the task or admin home page depending on user type.'''
    if current_user.email in admin_emails: # change in future iteration
        return redirect(url_for('main.admin'))
    return redirect(url_for('main.task'))

@main_blueprint.route('/task')
@login_required
def task():
    '''Display the task page for the student.'''
    student = User.query.filter_by(email=current_user.email).first()

    tasks = run_get_tasks_by_email(current_user.email)
    return render_template('task.html', tasks=tasks, student=student)

@main_blueprint.route('/subtask/<int:task_id>')
@login_required
def subtask(task_id):
    '''Display the subtask page for the student.'''
    # get all subtasks for a task
    subtasks = Subtask.query.filter_by(task_id=task_id).all()
    subtask_progress = {}
    for my_subtask in subtasks:
        subtask_progress[my_subtask] = get_subtask_status_by_progress(my_subtask)
    return render_template('subtask.html', subtasks=subtasks, subtask_progress=subtask_progress)

@main_blueprint.route('/steps/<int:subtask_id>')
@login_required
def steps(subtask_id):
    '''Display the steps page for the student.'''
    step_objects = Step.query.filter_by(subtask_id=subtask_id).all()
    my_steps = [{"id": step.id, "title": step.title, "content": step.content,
              "subtask_id": step.subtask_id} for step in step_objects]
    return render_template('steps.html', active_step=1, steps=my_steps)

@main_blueprint.route('/progress/<int:subtask_id>')
@login_required
def progress(subtask_id):
    '''Update the progress of the student on a subtask. 
    Called when the student clicks the submit button.'''
    # get the progress object for the user and subtask
    cur_progress = Progress.query.filter_by(user_id=current_user.id, subtask_id=subtask_id).first()

    # update the progress
    cur_progress.complete = True
    db.session.commit()

    return redirect(url_for('main.subtask', task_id=cur_progress.task_id))

@main_blueprint.route('/admin')
@login_required
def admin():
    '''Display the admin home page (all students page by default).'''
    users = User.query.all()
    students = []
    for user in users:
        if user.email not in admin_emails:
            students.append(user)
    # DYNAMICALLY DISPLAY TASKS FOR FUTURE USE
    return render_template('allStudents.html', students=students)
    # return render_template('allStudents.html')

@main_blueprint.route('/add_label', methods=['POST'])
@login_required
def add_label():
    '''Add a new label to the database. Called when the admin creates a label.'''
    label_name = request.json.get('labelName')
    label_color = request.json.get('labelColor')

    # Check if label name and color are provided
    if not label_name or not label_color:
        return jsonify({'error': 'Invalid input'}), 400

    # Check if the label already exists
    existing_label = Tag.query.filter_by(name=label_name).first()
    if existing_label:
        return jsonify({'error': 'Label already exists'}), 400

    # Create a new label and save to the database
    new_label = Tag(name=label_name, html_class=label_color)
    db.session.add(new_label)
    db.session.commit()

    return jsonify({'message': 'Label added successfully', 'label': {
        'name': label_name,
        'html_class': label_color
    }}), 200

@main_blueprint.route('/admin/updateTagsTasks', methods=['POST'])
@login_required
def update_tags_tasks():
    selected_emails_str = request.form.get('selectedStudentEmailsInput')
    item_name = request.form.get('itemName')
    item_type = request.form.get('itemType')
    action_type = request.form.get('actionType')
    print(f"Received data: {selected_emails_str}, Item: {item_name}, Type: {item_type}, Action: {action_type}")

    if selected_emails_str and item_name and item_type and action_type:
        selected_emails = selected_emails_str.split(",")  # Convert back to list
        print("Parsed list of emails:", selected_emails)
        # Perform the tag/task update logic here
        for email in selected_emails:
            user = User.query.filter_by(email=email).first()
            if user:
                if item_type == 'Tag':
                    tag = Tag.query.filter_by(name=item_name).first()
                    if tag:
                        if action_type == 'Assign' and tag not in user.tags:  # Prevent duplicate tag entries
                            user.tags.append(tag)
                        elif action_type == 'Remove' and tag in user.tags:  # Remove tag if it exists
                            user.tags.remove(tag)
                elif item_type == 'Task':
                    task = Task.query.filter_by(title=item_name).first()
                    if task:
                        if action_type == 'Assign' and task not in user.tasks:  # Prevent duplicate task entries
                            user.tasks.append(task)
                        elif action_type == 'Remove' and task in user.tasks:  # Remove task if it exists
                            user.tasks.remove(task)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        print("No data received.")
        return jsonify({'success': False, 'error': 'No data received'}), 400

@main_blueprint.route('/admin/addTask')
@login_required
def add_task():
    '''Display the add task page for the admin.'''
    return render_template('addTask.html')

@main_blueprint.route('/get_students_by_task')
def get_students_by_task():
    '''Get all students assigned to a task. Task is fetched by JS call in admin page.'''
    task_name = request.args.get('task')

    # Fetch the task by its title
    cur_task = Task.query.filter_by(title=task_name).first()

    if not cur_task:
        return jsonify({'error': 'Task not found'}), 404

    # Fetch all users assigned to this task using the user_task_association_table
    students = User.query.join(user_task_association_table).join(Task)\
                   .filter(Task.id == cur_task.id).all()

    students_data = []

    for student in students:
        # Get all subtasks for this task
        subtasks = Subtask.query.filter_by(task_id=cur_task.id).all()

        total_subtasks = len(subtasks)
        completed_subtasks = 0

        # Calculate progress for each student on the subtasks
        for cur_subtask in subtasks:
            # Fetch the progress for the student and subtask
            cur_progress = Progress.query.filter_by(user_id=student.id,
                                                    subtask_id=cur_subtask.id).first()
            if cur_progress and cur_progress.complete:
                completed_subtasks += 1

        # Calculate the progress percentage
        progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

        tags = Tag.query.join(user_tag_association_table).join(User).filter(User.id == student.id).all()
        serialized_tags = [{'name': tag.name, 'html_class': tag.html_class} for tag in tags]

        students_data.append({
            'email': student.email,
            'name' : student.name,
            "id": student.student_id,
            'tags': serialized_tags,
            'progress': {
                'completed': completed_subtasks,
                'total': total_subtasks,
                'percent': progress_percent
            }
        })

    return jsonify({'students': students_data})

@main_blueprint.route('/get_tags_for_student')
def get_tags_for_student():
    '''Get all tags assigned to a student. Student is fetched by JS call in admin page.'''
    student_name = request.args.get('student')

    # Fetch the student
    student = User.query.filter_by(name=student_name).first()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Fetch all users assigned to this task using the user_task_association_table
    tags = Tag.query.join(user_tag_association_table).join(User).filter(User.id == student.id).all()
    serialized_tags = [{'name': tag.name, 'html_class': tag.html_class} for tag in tags]

    return jsonify({'tags': serialized_tags})


@main_blueprint.route('/get_tags')
def get_tags():
    '''Get all tags from the database and returns as json.'''
    # Fetch all tags
    tags = Tag.query.order_by(Tag.name).all()

    if not tags:
        return jsonify({'error': 'Tag not found'}), 404

    # Serialize tags
    serialized_tags = [{'name': tag.name, 'html_class': tag.html_class} for tag in tags]

    return jsonify({'tags': serialized_tags})


@main_blueprint.route('/get_tasks')
def get_tasks():
    '''Get all tasks from the database and returns as json.'''
    # Fetch all tasks
    tasks = Task.query.all()

    if not tasks:
        return jsonify({'error': 'Task not found'}), 404

    # Serialize tasks
    serialized_tasks = [{'title': task.title} for task in tasks]

    return jsonify({'tasks': serialized_tasks})


@main_blueprint.route('/get_tasks_by_email')
def get_tasks_by_email():
    '''Accepts JS calls, runs run_get_tasks_by_email, and returns the result as json.'''
    email = request.args.get('email')
    return jsonify({'tasks': run_get_tasks_by_email(email)})

def run_get_tasks_by_email(email):
    '''Get all tasks assigned to a student by email. Can be called by python directly'''
    # get user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return []

    # get progress intances for the user
    cur_progress = Progress.query.filter_by(user_id=user.id).all()

    # get all unique tasks from task_id column in progress
    task_ids = set(progress_entry.task_id for progress_entry in cur_progress)

    tasks_data = []

    for task_id in task_ids:

        # get all subtasks in progress that have task_id
        subtasks = [progress_entry for progress_entry in cur_progress
                    if progress_entry.task_id == task_id]

        # get number of subtasks that are complete from subtasks
        completed_subtasks = sum(1 for subtask in subtasks if subtask.complete)

        # calculate progress as a percentage
        progress_percent = (completed_subtasks / len(subtasks)) * 100 if len(subtasks) > 0 else 0

        cur_task = Task.query.filter_by(id=task_id).first()

        tasks_data.append({
            'title': cur_task.title,
            'content': cur_task.content,
            'id': cur_task.id,
            'progress': {
                'completed': completed_subtasks,
                'total': len(subtasks),
                'percent': progress_percent
            }
        })
    return tasks_data


@main_blueprint.route('/admin/view_student_progress')
@login_required
def admin_view_student_progress():
    '''Display the progress of a student on a task for the admin.'''
    student_email = request.args.get('email')
    task_name = request.args.get('task_name')

    # Fetch the student and the task by name
    student = User.query.filter_by(email=student_email).first()
    if not student:
        return "Student not found", 404

    cur_task = Task.query.filter_by(title=task_name).first()
    if not cur_task:
        return "Task not found", 404

    # Fetch all subtasks for the task
    subtasks = Subtask.query.filter_by(task_id=cur_task.id).all()

    # Fetch progress for the student
    progress_data = Progress.query.filter_by(user_id=student.id, task_id=cur_task.id).all()

    # Create a dictionary of progress for fast lookup
    progress_dict = {progress.subtask_id: progress.complete for progress in progress_data}

    subtasks_progress = []
    for cur_subtask in subtasks:
        status = 'complete' if progress_dict.get(cur_subtask.id, False) else 'incomplete'
        subtasks_progress.append({
            'subtask': cur_subtask.title,
            'description': cur_subtask.content,  # Add description here
            'status': status
        })

    # Calculate overall progress
    completed_subtasks = sum(1 for subtask in subtasks_progress if subtask['status'] == 'complete')
    total_subtasks = len(subtasks)
    progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

    # Show progress as a ratio, e.g., "2 / 5"
    progress_ratio = f"{completed_subtasks} / {total_subtasks}"

    return render_template('adminViewStudentProgress.html', student=student, task=cur_task,
                           subtasks=subtasks_progress, progress_percent=progress_percent,
                           progress_ratio=progress_ratio)
@main_blueprint.route('/admin/addTask', methods=['POST'])
@login_required
def add_task_to_database():
    '''Add a new task to the database and assign it to all students.'''
    # Get form data
    task_name = request.form.get('task_name')
    deadline_str = request.form.get('deadline')
    subtask_titles = request.form.getlist('subtask_title[]')

    # Parse steps grouped by subtask index
    step_titles = {}
    step_contents = {}
    for key, value in request.form.items():
        if key.startswith('step_title['):
            subtask_index = int(key.split('[')[1].split(']')[0])
            step_titles.setdefault(subtask_index, []).append(value)
        elif key.startswith('step_content['):
            subtask_index = int(key.split('[')[1].split(']')[0])
            step_contents.setdefault(subtask_index, []).append(value)

    # Convert deadline to datetime
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None

    # Create the task
    cur_task = Task(title=task_name, content=f"Task created by {current_user.name}",
                    deadline=deadline)
    db.session.add(cur_task)
    db.session.commit()

    # Create subtasks and steps
    for subtask_index, subtask_title in enumerate(subtask_titles):
        cur_subtask = Subtask(title=subtask_title, content=f"Subtask for {task_name}",
                              task_id=cur_task.id)
        db.session.add(cur_subtask)
        db.session.commit()

        # Add all steps for the current subtask
        if subtask_index in step_titles and subtask_index in step_contents:
            for title, content in zip(step_titles[subtask_index], step_contents[subtask_index]):
                step = Step(
                    title=title,
                    content=content,
                    subtask_id=cur_subtask.id,
                    progress=0
                )
                db.session.add(step)
        db.session.commit()

    # Assign the task to all users
    all_users = User.query.all()  # Get all users from the database
    for user in all_users:
        user.tasks.append(cur_task)
    db.session.commit()

    return redirect(url_for('main.admin'))