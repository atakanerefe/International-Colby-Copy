'''Imports the create_app function from website package and runs the application in debug mode.'''
from website import create_app
from website.views import add_sample_data, add_task_ssn_application

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        add_sample_data()
        add_task_ssn_application()
    app.run(debug=True)
