# References:
# https://flask.palletsprojects.com/en/stable/patterns/appfactories/
# https://www.geeksforgeeks.org/python/__init__-in-python/
# https://medium.com/@ferrohardian/application-factory-pattern-starting-your-flask-project-

# This __init__ file is an application factory, it is a python constructor file and should be used that way

import os

from flask import Flask
from flask.cli import load_dotenv

def create_app(test_config=None):
    app = Flask(__name__)
    load_dotenv(".env")

    @app.route('/hello')
    def hello():
        return "Hello world"

    return app