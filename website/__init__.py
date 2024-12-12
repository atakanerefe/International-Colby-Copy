# The implementation Al Madi and us came up with requires global GOOGLE
# pylint: disable=global-variable-not-assigned
# The way we set up in class requires imports in create_app
# pylint: disable=import-outside-toplevel
'''Flask imports for building app, oauth for google login.
dotenv and os for environment variables, SQLAlchemy for database.'''
import os
from flask import Flask
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
# from .models import Progress, Subtask, Task, User, user_task_association_table
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
# werkzeug need to be werkzeug==2.3.7 if getting url error
# uninstall werkzeug and install werkzeug==2.3.7
load_dotenv()

GOOGLE = None
db = SQLAlchemy()

def create_app():
    '''Create app with configurations and register blueprints.'''
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        os.environ.get('DATABASE_URL').replace("postgres", "postgresql", 1)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    global GOOGLE
    GOOGLE = google_auth(app)

    from .models import User
    from .views import main_blueprint, get_subtask_status_by_progress
    from .auth import auth_blueprint

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprint for routes
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    #if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
        # add_sample_data() # harcoding data for demo
        #app.run(debug=True)

    @app.context_processor
    def jinjaHelper():
        # pylint does not recognize jinja formatting
        # pylint: disable=all
        def getSubtaskStatus(subtask):
            return get_subtask_status_by_progress(subtask)
        return dict(subtask_status = get_subtask_status_by_progress)

    return app

def google_auth(app):
    '''Google OAuth configuration for login.'''

    oauth = OAuth(app)

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

    return google

if __name__ == '__main__':
    create_app()