from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify, render_template, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import Subtask, Task, db, User
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
        if me.data['error']['status'] == 'UNAUTHENTICATED':
            return redirect(url_for('logout'))
        return loginUser(me.data)
        print(me.data)
        return render_template('task.html')
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
    if existing_user:
      # update to not double call database in the future
      login_user(existing_user)
    else:
      existing_user = User(email=userinfo['email'])
      db.session.add(existing_user)
      db.session.commit()
      login_user(existing_user)
    # print(existing_user.name)
    # if existing_user.name is None:
    #     print('name is none')
    #     return render_template('name_form.html')
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
    return render_template('task.html')

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

# adding sample data for demo
def add_sample_data():
    
    users_data = [
        "student1@example.com",
        "student2@example.com",
        "student3@example.com",
        "student4@example.com"
    ]
    
    # adding users if they don't exist in db
    for email in users_data:
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email=email)
            db.session.add(new_user)
            db.session.commit()

    # assigning emails to users
    user1 = User.query.filter_by(email="student1@example.com").first()
    user2 = User.query.filter_by(email="student2@example.com").first()
    user3 = User.query.filter_by(email="student3@example.com").first()
    user4 = User.query.filter_by(email="student4@example.com").first()

    # check if tasks already exist in db
    task1 = Task.query.filter_by(title="First Year Check In", user_id=user1.id).first()
    if not task1:
        # if not, add them
        task1 = Task(title="First Year Check In", content="First Year Check-In Task", progress=0, user_id=user1.id)
        db.session.add(task1)

    task2 = Task.query.filter_by(title="Social Security Number", user_id=user2.id).first()
    if not task2:
        task2 = Task(title="Social Security Number", content="SSN Task", progress=0, user_id=user2.id)
        db.session.add(task2)

    task3 = Task.query.filter_by(title="Employment: OPT/CPT", user_id=user3.id).first()
    if not task3:
        task3 = Task(title="Employment: OPT/CPT", content="OPT/CPT Task", progress=0, user_id=user3.id)
        db.session.add(task3)

    task4 = Task.query.filter_by(title="First Year Check In", user_id=user4.id).first()
    if not task4:
        task4 = Task(title="First Year Check In", content="First Year Check-In Task", progress=0, user_id=user4.id)
        db.session.add(task4)

    db.session.commit()

    # check if subtasks already exist in db
    # these are for task1
    subtask1 = Subtask.query.filter_by(title="Complete registration", task_id=task1.id).first()
    if not subtask1:
        subtask1 = Subtask(title="Complete registration", content="Fill out the registration form", complete=True, task_id=task1.id)
        db.session.add(subtask1)

    subtask2 = Subtask.query.filter_by(title="Submit documents", task_id=task1.id).first()
    if not subtask2:
        subtask2 = Subtask(title="Submit documents", content="Upload required documents", complete=False, task_id=task1.id)
        db.session.add(subtask2)

    subtask3 = Subtask.query.filter_by(title="Payment", task_id=task1.id).first()
    if not subtask3:
        subtask3 = Subtask(title="Payment", content="Complete payment for the semester", complete=True, task_id=task1.id)
        db.session.add(subtask3)

    # subtasks for task2
    subtask4 = Subtask.query.filter_by(title="Form submission", task_id=task2.id).first()
    if not subtask4:
        subtask4 = Subtask(title="Form submission", content="Submit form to the office", complete=False, task_id=task2.id)
        db.session.add(subtask4)

    subtask5 = Subtask.query.filter_by(title="Upload documents", task_id=task2.id).first()
    if not subtask5:
        subtask5 = Subtask(title="Upload documents", content="Upload proof of ID", complete=True, task_id=task2.id)
        db.session.add(subtask5)

    # subtasks for task3
    subtask6 = Subtask.query.filter_by(title="Fill application", task_id=task3.id).first()
    if not subtask6:
        subtask6 = Subtask(title="Fill application", content="Complete the OPT application", complete=True, task_id=task3.id)
        db.session.add(subtask6)

    subtask7 = Subtask.query.filter_by(title="Submit proof", task_id=task3.id).first()
    if not subtask7:
        subtask7 = Subtask(title="Submit proof", content="Submit necessary documents", complete=True, task_id=task3.id)
        db.session.add(subtask7)

    # subtasks for task4
    subtask8 = Subtask.query.filter_by(title="Complete registration", task_id=task4.id).first()
    if not subtask8:
        subtask8 = Subtask(title="Complete registration", content="Fill out the registration form", complete=False, task_id=task4.id)
        db.session.add(subtask8)

    subtask9 = Subtask.query.filter_by(title="Submit documents", task_id=task4.id).first()
    if not subtask9:
        subtask9 = Subtask(title="Submit documents", content="Upload required documents", complete=True, task_id=task4.id)
        db.session.add(subtask9)

    db.session.commit()

@app.route('/get_students_by_task')
def get_students_by_task():
    task_name = request.args.get('task')

    # getting tasks based on task name
    task = Task.query.filter_by(title=task_name).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # getting users
    users = User.query.all()

    students_data = []
    seen_students = set()

    for user in users:
        # find tasks assigned to user
        user_tasks = Task.query.filter_by(user_id=user.id, title=task_name).all()

        for user_task in user_tasks:
            # get all subtasks related to this task
            subtasks = Subtask.query.filter_by(task_id=user_task.id).all()

            total_subtasks = len(subtasks)
            completed_subtasks = sum(1 for subtask in subtasks if subtask.complete)

            # calculate progress as a percentage
            progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

            # check if the student has already been added
            if user.email not in seen_students:
                seen_students.add(user.email)
                students_data.append({
                    'email': user.email,
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

    # get user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # get tasks assigned to user
    tasks = Task.query.filter_by(user_id=user.id).all()

    tasks_data = []

    for task in tasks:
        # get all subtasks related to this task
        subtasks = Subtask.query.filter_by(task_id=task.id).all()

        total_subtasks = len(subtasks)
        completed_subtasks = sum(1 for subtask in subtasks if subtask.complete)

        # calculate progress as a percentage
        progress_percent = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

        tasks_data.append({
            'title': task.title,
            'content': task.content,
            'progress': {
                'completed': completed_subtasks,
                'total': total_subtasks,
                'percent': progress_percent
            }
        })
    return jsonify({'tasks': tasks_data})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
        add_sample_data() # harcoding data for demo
    app.run(debug=True)