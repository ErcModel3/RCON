# References:
# https://flask.palletsprojects.com/en/stable/tutorial/views/
# https://www.geeksforgeeks.org/python/flask-blueprints/

from flask import Blueprint

bp = Blueprint('blueprint', __name__)

@bp.route('/hello')
def hello():
    return "Hello world"