from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, ValidationError

from app.models import db, Role, User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message='Это поле является обязательным.')])
    password = PasswordField("Password", validators=[DataRequired(message='Это поле является обязательным.')])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message='Это поле является обязательным.')],
                       render_kw={"autocomplete": "off"})
    username = StringField("Username", validators=[DataRequired(message='Это поле является обязательным.')],
                           render_kw={"autocomplete": "off"})
    email = StringField("Email", render_kw={"autocomplete": "off"})
    role = SelectField('Role', default=0, validators=[DataRequired(message='Это поле является обязательным.')],
                       coerce=int)

    password = PasswordField("Password")
    password_replay = PasswordField("Password_replay")

    submit = SubmitField("Submit")

    def validate_password(self, password):
        if not self._mode:
            if not password.data.strip() or password.data != self.password_replay.data:
                raise ValidationError('Пароли не равны или пароль пуст.')

    def validate_username(self, username):
        if not self._mode:
            if db.session.query(User).filter(User.username==username.data).first():
                raise ValidationError('Имя пользователя уже есть.')
        else:
            if self._mode.username != username.data:
                if db.session.query(User).filter(User.username == username.data).first():
                    raise ValidationError('Имя пользователя уже есть')

    def __init__(self, mode, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mode = mode
        self._user = user
        if user:
            self.user_id = user.id
            self.name.data = self._user.name
            self.username.data = self._user.username
            self.role.data = self._user.role.id

        self.role.choices = Role.choices()


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(message='Это поле является обязательным.')])
    password_replay = PasswordField("Password_replay",
                                    validators=[DataRequired(message='Это поле является обязательным.')])
    submit = SubmitField("Submit")

    def validate_password(self, password):
        if password.data != self.password_replay.data:
            raise ValidationError('Passwords are not equal')
