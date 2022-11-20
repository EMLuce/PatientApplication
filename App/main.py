"""
This is the main python file that runs the website.
"""
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)