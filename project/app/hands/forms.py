from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, TextAreaField, \
    SelectField, DateField
from wtforms.validators import DataRequired, ValidationError, Length
