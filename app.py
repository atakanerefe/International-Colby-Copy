from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify, render_template, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import Progress, Subtask, Task, db, User, user_task_association_table
import os
from dotenv import load_dotenv
# werkzeug need to be werkzeug==2.3.7 if getting url error
# uninstall werkzeug and install werkzeug==2.3.7
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres", "postgresql", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

ADMIN_EMAILS = [
    "mbeltguz@colby.edu",
    "aemoreno@colby.edu",
    "mfreese@colby.edu"
]

oauth = OAuth(app)

# google_redirect_uri = 'http://127.0.0.1:5000/login/authorized' # change to your computer port
google_redirect_uri = 'https://intapp-f95d32a0df1a.herokuapp.com/login/authorized'

google = oauth.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_CLIENT_ID'),
    consumer_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={'scope': 'email',},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

login_manager = LoginManager(app)
login_manager.login_view = '/'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        # print(me.data)
        # print(me.data['error']['status'])
        # if me.data['error']['status'] == 'UNAUTHENTICATED':
        #     return redirect(url_for('logout'))
        # return loginUser(me.data)
        # print(me.data)
        print(current_user.get_id())
        return render_template('task.html', tasks=run_get_tasks_by_email(me.data['email']))
    return 'Hello! Log in with your Google account: <a href="/login">Log in</a>'

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    me = google.get('userinfo')
    loginUser(me.data)
    # Here, 'me.data' contains user information.
    # You can perform registration process using this information if needed.

    return redirect(url_for('task'))

def loginUser(userinfo):
    existing_user = User.query.filter_by(email=userinfo['email']).first()
    if not existing_user:
      existing_user = User(email=userinfo['email'])
      db.session.add(existing_user)
      db.session.commit()
    login_user(existing_user)
    # print(existing_user.name)
    # if existing_user.name is None:
    #     print('name is none')
    #     return render_template('name_form.html')

    if existing_user.email in ADMIN_EMAILS:
        return redirect(url_for('admin')) 
    
    return redirect(url_for('task'))

@app.route('/finish-login')
def finish_login():
    return render_template('name_form.html')

@app.route('/logout')
def logout():
    logout_user()
    session.pop('google_token', None)
    return redirect(url_for('index'))
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/task')
@login_required
def task():
    return render_template('task.html', tasks=get_tasks_by_email(current_user.email))

@app.route('/subtask')
@login_required
def subtask():
    return render_template('subtask.html')

@app.route('/steps')
@login_required
def steps():
    step = request.args.get('step', default=1, type=int)
    return render_template('steps.html', active_step=step)

@app.route('/admin')
@login_required
def admin():
    return render_template('admin_home.html')

@app.route('/admin/addTask')
@login_required
def addTask():
    return render_template('addTask.html')

def add_sample_data():
    # Create or fetch users
    users_data = [
        "obraym25@colby.edu",
        "student2@example.com",
        "student3@example.com",
        "student4@example.com"
    ]

    # Add users if they don't already exist in the database
    users = []
    for email in users_data:
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email=email)
            db.session.add(new_user)
            users.append(new_user)
        else:
            users.append(existing_user)
    db.session.commit()

    # Fetch the users dynamically
    user_ids = [user.id for user in users]

    # Create a task (this task can be assigned to multiple users)
    task = Task.query.filter_by(title="Sample Task").first()
    if not task:
        task = Task(title="Sample Task", content="This is a sample task.")
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
        {"title": "Subtask 1", "content": "Description for Subtask 1"},
        {"title": "Subtask 2", "content": "Description for Subtask 2"},
        {"title": "Subtask 3", "content": "Description for Subtask 3"},
        {"title": "Subtask 4", "content": "Description for Subtask 4"},
        {"title": "Subtask 5", "content": "Description for Subtask 5"}
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


@app.route('/get_students_by_task')
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

@app.route('/get_tasks_by_email')
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
        add_sample_data() # harcoding data for demo
    app.run(debug=True)