from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_on = db.Column(db.DateTime(), default=datetime.now)
    updated_on = db.Column(db.DateTime(), default=datetime.now,  onupdate=datetime.now)

    users = db.relationship('User', backref='role')

    @classmethod
    def insert_roles(cls):
        for permission in app.config['PERMISSION']:
            role = cls(name=permission)
            db.session.add(role)
            db.session.commit()

    @classmethod
    def choices(cls):
        r = [(role.id, role.name) for role in db.session.query(cls).all()]
        r.append((0, ''))
        return r


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)
    updated_on = db.Column(db.DateTime(), default=datetime.now,  onupdate=datetime.now)

    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_administrator(self):
        if self.role.name == 'admin':
            return True

    @property
    def is_moderator(self):
        if self.role.name in ['moderator', 'admin']:
            return True

    @property
    def is_user(self):
        if self.role.name == 'user':
            return True

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)
