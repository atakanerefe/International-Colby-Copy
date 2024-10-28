from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # tasks = db.relationship('Task', backref='user')

# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(80), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     subtasks = db.relationship('Subtask', backref='user')

# class Subtask(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(80), nullable=False)
#     task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
#     steps = db.relationship('Step', backref='user')

# class Step(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(80), nullable=False)
#     subtask_id = db.Column(db.Integer, db.ForeignKey('subtask.id'))
#     status = db.Column(db.Boolean, default=False)
#     subtasks = db.relationship('Subtask', backref='user')



