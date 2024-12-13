'''Imports the create_app function from website package and runs the application in debug mode.'''
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
