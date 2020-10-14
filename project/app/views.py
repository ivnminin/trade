from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app
from flask_login import login_required, login_user, current_user, logout_user

from app import app, db
from app.models import User, NameTask
from app.backend import logger_app
from app.backend.tasker import send_email

from .forms import ConsultationForm


@app.route("/",  methods=["GET", "POST"])
def index():

    form = ConsultationForm()
    if request.method == "POST" and form.validate_on_submit():

        subject = "Запрос"
        body = "{}\n{}\n{}".format(form.name.data, form.description.data, form.contact_data.data)
        sender = current_app.config["MAIL_USERNAME"]
        recipients = [current_app.config["MAIL_ADMIN"], ]

        try:
            job = send_email.apply_async(args=[subject, body, sender, recipients], countdown=3)
            # r = job.get()

            flash("Запрос создан, ожидайте ответ. Спасибо.", "success")
            # return make_response(r)

            return redirect(url_for("index"))
        except Exception as e:
            logger_app.error("{} :{}".format(NameTask.sending_email.name, e))
            flash("Запрос НЕ создан, что то пошло не так.", "error")

            return redirect(url_for("index"))



    return render_template("frontend/index.html", form=form)
