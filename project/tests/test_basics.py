import unittest
from flask import current_app
from app import app, db

class BasicsCaseTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app_context = app.app_context()
        self.app_context.push()
        # db.create_all()

    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)
