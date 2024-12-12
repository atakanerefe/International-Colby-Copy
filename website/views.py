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
    if not student:
        return "Student not found", 404
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
    if not cur_progress:
        return "Progress not found", 404

    # update the progress
    cur_progress.complete = True
    db.session.commit()

    return redirect(url_for('main.subtask', task_id=cur_progress.task_id))

@main_blueprint.route('/admin')
@login_required
def admin():
    '''Display the admin home page (all students page by default).'''
    student = User.query.filter_by(email=current_user.email).first()
    # DYNAMICALLY DISPLAY TASKS FOR FUTURE USE
    return render_template('allStudents.html', tasks=Task.query.all(), student=student)
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
    students = User.query.join(user_task_association_table).join(Task).filter(Task.id == cur_task.id).all()

    students_data = []

    for student in students:
        # Get all subtasks for this task
        subtasks = Subtask.query.filter_by(task_id=cur_task.id).all()

        total_subtasks = len(subtasks)
        completed_subtasks = 0

        # Calculate progress for each student on the subtasks
        for cur_subtask in subtasks:
            # Fetch the progress for the student and subtask
            cur_progress = Progress.query.filter_by(user_id=student.id, subtask_id=cur_subtask.id).first()
            if cur_progress and cur_progress.complete:
                completed_subtasks += 1

        # Calculate the progress percentage
        progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

        students_data.append({
            'email': student.email,
            'name' : student.name,
            "id": student.student_id,
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
    tags = Tag.query.all()

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
    '''Get all tasks assigned to a student by email. Email is fetched by JS call in task page.'''
    email = request.args.get('email')
    return jsonify({'tasks': run_get_tasks_by_email(email)})

def run_get_tasks_by_email(email):
   # get user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # get progress intances for the user
    cur_progress = Progress.query.filter_by(user_id=user.id).all()

    # get all unique tasks from task_id column in progress
    task_ids = set(progress_entry.task_id for progress_entry in cur_progress)

    tasks_data = []

    for task_id in task_ids:
        
        # get all subtasks in progress that have task_id
        subtasks = [progress_entry for progress_entry in cur_progress if progress_entry.task_id == task_id]
        
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
def adminViewStudentProgress():
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
    '''Add a new task to the database. Called when the admin aubmits add task form.'''
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
    db.session.add(task)
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

    return redirect(url_for('main.admin'))


def add_sample_data():
    '''Add sample data to the database for testing purposes.'''
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

    # Create a task (this task can be assigned to multiple users)
    cur_task = Task.query.filter_by(title="First Year Check In").first()
    if not cur_task:
        cur_task = Task(title="First Year Check In", content="This is a sample task.")
        db.session.add(cur_task)
        db.session.commit()

    # Check if the user-task association already exists before adding
    # Set of user IDs already associated with this task
    existing_users_in_task = set(user.id for user in cur_task.users)
    users_to_add = [user for user in users if user.id not in existing_users_in_task]

    if users_to_add:
        # Add users who are not yet associated with the task
        for user in users_to_add:
            cur_task.users.append(user)
        db.session.commit()

    # repeat for task2
    task2 = Task.query.filter_by(title="Get Social Security Number").first()
    if not task2:
        task2 = Task(title="Get Social Security Number", content="This is a second sample task.")
        db.session.add(task2)
        db.session.commit()

    existing_users_in_task2 = set(user.id for user in task2.users) 
    # print("task2 existing users: ", existing_users_in_task2)
    user_to_add_task2 = User.query.filter_by(name="Tricia").first()
    # print("Tricia to add: ", user_to_add_task2)

    if user_to_add_task2:
        if user_to_add_task2.id not in existing_users_in_task2:
            # Add users who are not yet associated with the task
            task2.users.append(user_to_add_task2)
        db.session.commit()


    # Create subtasks and assign them to the task
    subtasks_data = [
        {"title": "I-20 Signature", "content": 
         "Go to Aura Moreno's office in Cotter Union 239 to get your I-20 signed."},
        {"title": "Get US Phone Number", "content": 
         "Pick up a SIM card from the Pugh Center or use a free Google Voice number."},
        {"title": "Bla Bla Bla 1", "content": "Bla Bla Bla 1"},
        {"title": "Bla Bla Bla 2", "content": "Bla Bla Bla 2"},
        {"title": "Bla Bla Bla 3", "content": "Bla Bla Bla 3"},
    ]

    steps_data = [
        {"title": "Step 1", "content": "Bsdkfmksdf"},
        {"title": "Step 2", "content": "sdv,sdlvsd"},
        {"title": "Step 3", "content": "sdvkmsdmfmg"},
        {"title": "Step 4", "content": "grekmtmrkey"},
        {"title": "Step 5", "content": "sef,k,lrdkg"},
    ]

    subtasks = []
    steps_list = []
    for subtask_data in subtasks_data:
        cur_subtask = Subtask.query.filter_by(title=subtask_data["title"], 
                                              task_id=cur_task.id).first()

        if not cur_subtask:
            cur_subtask = Subtask(title=subtask_data["title"], content=subtask_data["content"], 
                                  task_id=cur_task.id)
            db.session.add(cur_subtask)
            subtasks.append(cur_subtask)

    for cur_subtask in subtasks:
        for step_data in steps_data:
            step = Step.query.filter_by(title=step_data["title"], subtask_id=cur_subtask.id).first()
            if not step:
                step = Step(title=step_data["title"], content=step_data["content"], 
                            subtask_id=cur_subtask.id, progress=0)
                db.session.add(step)
                steps_list.append(step)

    db.session.commit()

    # Track progress for each user on the same task
    progress_data = [
        {"user": users[0], "subtasks_completed": [1, 2, 3]},  # User 1 has completed subtasks 1,2,3
        {"user": users[1], "subtasks_completed": [2, 4]},     # User 2 has completed subtasks 2,4
        {"user": users[2], "subtasks_completed": [3, 5]},     # User 3 has completed subtasks 3,5
        {"user": users[3], "subtasks_completed": [1, 4, 5]}    # User 4 has completed subtasks 1,4,5
    ]

    # For each user, create progress records for their respective subtasks
    for progress_entry in progress_data:
        user = progress_entry["user"]
        for i, subtask in enumerate(subtasks):
            cur_progress = Progress.query.filter_by(user_id=user.id, subtask_id=subtask.id).first()
            if not cur_progress:
                complete = True if i + 1 in progress_entry["subtasks_completed"] else False
                cur_progress = Progress(complete=complete, user_id=user.id, 
                                        subtask_id=subtask.id, task_id=cur_task.id)
                db.session.add(cur_progress)
    db.session.commit()

    # creating tags uniquely
    # TAG 1
    tag1 = Tag.query.filter_by(name="tag1").first()
    if not tag1:
        tag1 = Tag(name="tag1", html_class="bg-warning")
        db.session.add(tag1)
        db.session.commit()

    # TAG 2
    tag2 = Tag.query.filter_by(name="tag2").first()
    if not tag2:
        tag2 = Tag(name="tag2", html_class="bg-warning")
        db.session.add(tag2)
        db.session.commit()

    # assign to two users
    existing_users_with_tag1 = set(user.id for user in tag1.users) 
    existing_users_with_tag2 = set(user.id for user in tag2.users) 
    # print("task2 existing users: ", existing_users_in_task2)
    user1_to_add_tag1 = User.query.filter_by(name="Tricia").first()
    user2_to_add_tag1 = User.query.filter_by(name="Owen").first()
    user1_to_add_tag2 = User.query.filter_by(name="Tricia").first()
    # print("Tricia to add: ", user_to_add_task2)

    if user1_to_add_tag1:
        if user1_to_add_tag1.id not in existing_users_with_tag1:
            # Add users who are not yet associated with the task
            tag1.users.append(user1_to_add_tag1)
            db.session.commit()

    if user2_to_add_tag1:
        if user2_to_add_tag1.id not in existing_users_with_tag1:
            tag1.users.append(user2_to_add_tag1)
            db.session.commit()

    if user1_to_add_tag2:
        if user1_to_add_tag2.id not in existing_users_with_tag2:
            # Add users who are not yet associated with the task
            tag2.users.append(user1_to_add_tag2)
            db.session.commit()
