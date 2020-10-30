from app import db
from . import backend
from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from app.models import db, User, TypeDealer, NameTask, Task, Category, Position, Characteristic, Image
from .forms import LoginForm
from .tasker import update_category, update_position, test_task, send_email
from . import logger_app


@backend.route("/backend/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        try:
            # job = gen_prime.apply_async(args=[100], countdown=3)
            # r = job.get()
            # # job = gen_prime(100)
            #
            # return make_response(", ".join(map(lambda x: str(x), r)))
            # job = update_category.apply_async(args=[], countdown=3)

            job = test_task.apply_async(args=[], countdown=3)
            r = job.get()

            return make_response(r)

        except Exception as e:

            return make_response(str(e))


    return render_template("backend/index.html")


@backend.route("/backend/category", methods=["GET", "POST"])
def category():

    categories = db.session.query(Category).order_by(Category.id).all()

    return render_template("backend/category.html", categories=categories)


@backend.route("/backend/category/turn/<id>")
def category_turn(id):
    category = db.session.query(Category).filter(Category.id == id).first_or_404()

    if request.args.get("turn") == "on":
        turn = True
    else:
        turn = False

    category.turn = turn
    db.session.add(category)
    db.session.commit()

    categories = []
    for category in category.get_subcategories():
        category.turn = turn
        categories.append(category)

    db.session.add_all(categories)
    db.session.commit()

    flash("Директория включена" if turn else "Директория отключена", "success")
    return redirect(url_for("backend.category"))


@backend.route("/backend/task/category", methods=["GET", "POST"])
def task_category():

    if request.method == "POST":

        try:
            job = update_category.apply_async(args=[], countdown=3)

            return redirect(url_for("backend.task_category"))
        except Exception as e:

            logger_app.error("{} :{}".format(NameTask.updating_structure_of_catalog.name, e))

    tasks = db.session.query(Task).filter(Task.name == NameTask.updating_structure_of_catalog.value)\
                                  .order_by(Task.timestamp_created.desc()).all()

    return render_template("backend/task_category.html", tasks=tasks)


@backend.route("/backend/position", methods=["GET", "POST"])
def position():

    positions = db.session.query(Position).order_by(Position.id).all()

    return render_template("backend/position.html", positions=positions)


@backend.route("/backend/task/position", methods=["GET", "POST"])
def task_position():

    if request.method == "POST":
        try:
            job = update_position.apply_async(args=[], countdown=3)

            return redirect(url_for("backend.task_position"))
        except Exception as e:

            logger_app.error("{} :{}".format(NameTask.updating_positions.name, e))

    tasks = db.session.query(Task).filter(Task.name == NameTask.updating_positions.value)\
                                  .order_by(Task.timestamp_created.desc()).all()

    return render_template("backend/task_position.html", tasks=tasks)