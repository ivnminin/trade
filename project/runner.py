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

@app.cli.command("test_coverage")
def coverage():
    """
    Run tests using the coverage module
    """

    import os
    import coverage
    import unittest

    cov = coverage.coverage(branch=True, source="app/*")
    cov.start()
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print("Coverage summary:")
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    cov_dir = os.path.join(basedir, "coverage")
    cov.html_report(directory=cov_dir)
    cov.erase()


if __name__ == "__main__":
    manager.run()