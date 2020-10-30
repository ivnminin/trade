import os

from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager
from flask_redis import FlaskRedis
from werkzeug.debug import DebuggedApplication
from celery import Celery

import config

app = Flask(__name__)
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

app.config.from_object(os.environ.get("FLASK_ENV") or "config.DevelopementConfig")


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend= app.config["REDIS_URL"],
        broker= app.config["RABBITMQ_URL"],
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

redis_client = FlaskRedis(app)
redis_client.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

from .backend import backend as backend_blueprint
app.register_blueprint(backend_blueprint)

from . import views
