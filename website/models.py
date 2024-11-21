from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from website import db

user_task_association_table = db.Table('user_task_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    tasks = db.relationship('Task', secondary=user_task_association_table, backref=db.backref('users', lazy='dynamic'))
    progress = db.relationship('Progress', backref='user')

    # implement get_id method
    def get_id(self):
        return str(self.id)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    subtasks = db.relationship('Subtask', backref='task')

class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    steps = db.relationship('Step', backref='subtask')

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    subtask_id = db.Column(db.Integer, db.ForeignKey('subtask.id'), nullable=False)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complete = db.Column(db.Boolean, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    subtask_id = db.Column(db.Integer, db.ForeignKey('subtask.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# def add_sample_data():
#     # Create or fetch users
#     users_data = [
#         "obraym25@colby.edu",
#         "ybmold25@colby.edu",
#         "pyang25@colby.edu",
#         "aerefe26@colby.edu"
#     ]

#     # Add users if they don't already exist in the database
#     users = []
#     for email in users_data:
#         existing_user = User.query.filter_by(email=email).first()
#         if not existing_user:
#             new_user = User(email=email)
#             db.session.add(new_user)
#             users.append(new_user)
#         else:
#             users.append(existing_user)
#     db.session.commit()

#     # Fetch the users dynamically
#     user_ids = [user.id for user in users]

#     # Create a task (this task can be assigned to multiple users)
#     task = Task.query.filter_by(title="First Year Check In").first()
#     if not task:
#         task = Task(title="First Year Check In", content="This is a sample task.")
#         db.session.add(task)
#         db.session.commit()

#     # Check if the user-task association already exists before adding
#     existing_users_in_task = set(user.id for user in task.users)  # Set of user IDs already associated with this task
#     users_to_add = [user for user in users if user.id not in existing_users_in_task]

#     if users_to_add:
#         # Add users who are not yet associated with the task
#         for user in users_to_add:
#             task.users.append(user)
#         db.session.commit()

#     # Create subtasks and assign them to the task
#     subtasks_data = [
#         {"title": "I-20 Signature", "content": "Go to Aura Moreno's office in Cotter Union 239 to get your I-20 signed."},
#         {"title": "Get US Phone Number", "content": "Pick up a SIM card from the Pugh Center or use a free Google Voice number."},
#         {"title": "Bla Bla Bla 1", "content": "Bla Bla Bla 1"},
#         {"title": "Bla Bla Bla 2", "content": "Bla Bla Bla 2"},
#         {"title": "Bla Bla Bla 3", "content": "Bla Bla Bla 3"},
#     ]

#     subtasks = []
#     for subtask_data in subtasks_data:
#         subtask = Subtask.query.filter_by(title=subtask_data["title"], task_id=task.id).first()
#         if not subtask:
#             subtask = Subtask(title=subtask_data["title"], content=subtask_data["content"], task_id=task.id)
#             db.session.add(subtask)
#             subtasks.append(subtask)
#     db.session.commit()

#     # Track progress for each user on the same task
#     progress_data = [
#         {"user": users[0], "subtasks_completed": [1, 2, 3]},  # User 1 has completed subtasks 1, 2, 3
#         {"user": users[1], "subtasks_completed": [2, 4]},     # User 2 has completed subtasks 2, 4
#         {"user": users[2], "subtasks_completed": [3, 5]},     # User 3 has completed subtasks 3, 5
#         {"user": users[3], "subtasks_completed": [1, 4, 5]}    # User 4 has completed subtasks 1, 4, 5
#     ]

#     # For each user, create progress records for their respective subtasks
#     for progress_entry in progress_data:
#         user = progress_entry["user"]
#         for i, subtask in enumerate(subtasks):
#             progress = Progress.query.filter_by(user_id=user.id, subtask_id=subtask.id).first()
#             if not progress:
#                 complete = True if (i + 1) in progress_entry["subtasks_completed"] else False
#                 progress = Progress(complete=complete, user_id=user.id, subtask_id=subtask.id, task_id=task.id)
#                 db.session.add(progress)
#     db.session.commit()