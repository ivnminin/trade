import os
from app import db, create_app
from app.models import Role, User
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand


app = create_app(os.getenv('FLASK_ENV') or 'config.DevelopementConfig')

manager = Manager(app)

# these names will be available inside the shell without explicit import
@app.shell_context_processor
def make_shell_context():
    return dict(app=app,  db=db, Role=Role, User=User)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()