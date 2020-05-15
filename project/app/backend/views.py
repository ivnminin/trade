from app import db
from . import backend
from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app
from flask_login import login_required, login_user, current_user, logout_user
from app.models import db, User, TypeDealer, NameTask, Task, Category
from .forms import LoginForm
from .waiter import update_category, gen_prime
from . import NLReceiver, logger_dealer_nl


@backend.route("/backend/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        try:
            # job = gen_prime.apply_async(args=[100], countdown=3)
            # r = job.get()
            # # job = gen_prime(100)
            #
            # return make_response(", ".join(map(lambda x: str(x), r)))
            job = update_category.apply_async(args=[], countdown=3)
            r = job.get()

            return make_response(r)

        except Exception as e:

            return make_response(str(e))


    return render_template("backend/index.html")


@backend.route("/backend/category", methods=["GET", "POST"])
def category():

    categories = db.session.query(Category).all()

    return render_template("backend/category.html", categories=categories)


@backend.route("/backend/task/category", methods=["GET", "POST"])
def task_category():

    if request.method == "POST":

        try:
            job = update_category.apply_async(args=[], countdown=3)
            return redirect(url_for('backend.task_category'))
        except Exception as e:

            logger_dealer_nl.error("{} :{}".format(NameTask.updating_structure_of_catalog.name, e))

    tasks = db.session.query(Task).filter(Task.name == NameTask.updating_structure_of_catalog.value)\
                                  .order_by(Task.timestamp_created.desc()).all()

    return render_template("backend/task_category.html", tasks=tasks)