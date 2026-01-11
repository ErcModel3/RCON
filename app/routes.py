"""
References:
https://flask.palletsprojects.com/en/stable/tutorial/views/
https://www.geeksforgeeks.org/python/flask-blueprints/
https://flask.palletsprojects.com/en/stable/quickstart/#routing
"""

from flask import Blueprint, request, render_template 

rcon = Blueprint('blueprint', __name__)

# Combined html api requests should be done using rcon.route()
@rcon.get('/')
@rcon.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return get_login()
    else:
        return post_login()

@rcon.post('/logout')
def logout():
    return "logout page"

@rcon.route('/console')
def console():
    return render_template ("console.j2")

@rcon.route('/hello')
def hello():
    """
    First route as a guideline
    """
    return "Hello world"

def get_login():
    return render_template ("base.html")
    # return "get login"
    
def post_login():
    return "post login"