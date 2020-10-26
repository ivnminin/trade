from app import app, db
from app.models import Role, User
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand


manager = Manager(app)

# these names will be available inside the shell without explicit import
@app.shell_context_processor
def make_shell_context():
    return dict(app=app,  db=db, Role=Role, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

@app.cli.command("create_db")
def create_db():
    """
    create_db >>>db.create_all()
    """

    db.create_all()

@app.cli.command("test")
def test():
    """
    Run tests
    """

    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()