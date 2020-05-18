from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, TextAreaField, \
    SelectField, DateField
from wtforms.validators import DataRequired, ValidationError, Length


class ConsultationForm(FlaskForm):
    name = StringField("Name", default="", validators=[DataRequired(message="Это поле является обязательным."),
                        Length(max=255, message="Длина поля не может превышать 250 символов.")],
                        render_kw={"autocomplete": "off"})
    description = TextAreaField("Description",
                                validators=[DataRequired(message="Это поле является обязательным."),
                                            Length(max=1024, message="Длина поля не может превышать 1024 символов.")],
                                render_kw={"rows": 4, "cols": 50})
    contact_data = StringField("ContactData",
                               validators=[DataRequired(message="Это поле является обязательным."),
                               Length(max=255, message="Длина поля не может превышать 250 символов.")],
                               render_kw={"autocomplete": "off"})

    submit = SubmitField("Submit")