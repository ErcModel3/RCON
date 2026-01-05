"""
References:
https://flask.palletsprojects.com/en/stable/tutorial/views/
https://www.geeksforgeeks.org/python/flask-blueprints/
https://flask.palletsprojects.com/en/stable/quickstart/#routing
"""

from flask import Blueprint, request

rcon = Blueprint('blueprint', __name__)

@rcon.get('/')
def index():
    return "Index page"

# Combined html api requests should be done using rcon.route()
@rcon.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return get_login()
    else:
        return post_login()

@rcon.post('/logout')
def logout():
    return "logout page"

@rcon.route('/hello')
def hello():
    """
    First route as a guideline
    """
    return "Hello world"

def get_login():
    return "get login"
    
def post_login():
    return "post login"