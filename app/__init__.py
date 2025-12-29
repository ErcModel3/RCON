"""
https://flask.palletsprojects.com/en/stable/patterns/appfactories/
https://www.geeksforgeeks.org/python/__init__-in-python/
https://medium.com/@ferrohardian/application-factory-pattern-starting-your-flask-project-
"""
# This __init__ file is an application factory

import os
from flask import Flask
from flask.cli import load_dotenv

def create_app():
    """
    Main create app function, used as a constructor
    """
    app = Flask(__name__)
    load_dotenv(".env")

    from . import routes # pylint: disable=import-outside-toplevel
    app.register_blueprint(routes.bp)

    return app
