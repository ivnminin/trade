import click

from flask_script import Manager, Shell
from flask_migrate import MigrateCommand

from app import app, db
from app.models import Role, User


manager = Manager(app)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.cli.command('start-project')
def start_project():
    """
    start project start-project >>>db.create_all()
    """
    db.create_all()


@app.cli.command('create-role')
def create_role():
    """
    flask project create-role
    """
    Role.insert_roles()


@app.cli.command('fake-data')
def fake_data():
    """
    flask fake-data
    """


@app.cli.command('registration-user')
@click.argument('name')
@click.argument('username')
@click.argument('password')
def registration_user(name, username, password):
    """
    registration user registration-user - <name> <user_name> <password>
    """

    user = User(name=name, username=username, password=password)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
