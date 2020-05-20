import os

from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager
from werkzeug.debug import DebuggedApplication
from celery import Celery

import config

app = Flask(__name__)
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

app.config.from_object(os.environ.get("FLASK_ENV") or "config.DevelopementConfig")


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend="redis://redis_trade:6379/0",
        broker="amqp://myuser1:mypass1@rabbitmq_trade:5672/myvhost1",
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = make_celery(app)

csrf = CsrfProtect()
csrf.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app,  db)

mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

from .backend import backend as backend_blueprint
app.register_blueprint(backend_blueprint)

from .hands import hands as hands_blueprint
app.register_blueprint(hands_blueprint, url_prefix="/hands")

from . import views