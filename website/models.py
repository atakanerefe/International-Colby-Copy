# Our database models do not need methods
#pylint: disable=too-few-public-methods
'''Get database from website and user helper from flask'''
from flask_login import UserMixin
from website import db

user_task_association_table = db.Table('user_task_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'))
)

user_tag_association_table = db.Table('user_tag_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class User(db.Model, UserMixin):
    '''User class that contains information for admin and students.'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    student_id = db.Column(db.Integer, nullable=True)
    tasks = db.relationship('Task', secondary=user_task_association_table,
                            backref=db.backref('users', lazy='dynamic'))
    progress = db.relationship('Progress', backref='user')
    tags = db.relationship('Tag', secondary=user_tag_association_table,
                           backref=db.backref('users', lazy='dynamic'))

    # implement get_id method
    def get_id(self):
        return str(self.id)

class Task(db.Model):
    '''Task class that contains information for tasks.'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    subtasks = db.relationship('Subtask', backref='task')

class Subtask(db.Model):
    '''Subtask class that contains information for subtasks.'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    steps = db.relationship('Step', backref='subtask')

class Step(db.Model):
    '''Step class that contains information for steps.'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    subtask_id = db.Column(db.Integer, db.ForeignKey('subtask.id'), nullable=False)

class Progress(db.Model):
    '''Progress class that contains information for progress of tasks.'''
    id = db.Column(db.Integer, primary_key=True)
    complete = db.Column(db.Boolean, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    subtask_id = db.Column(db.Integer, db.ForeignKey('subtask.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Tag(db.Model):
    '''Tag class that contains information for tags.'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    html_class = db.Column(db.String(120), nullable=False)
