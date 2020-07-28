from app import db
from . import backend
from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from app.models import db, User, TypeDealer, NameTask, Task, Category, Position, Characteristic, Image
from .forms import LoginForm
from .waiter import update_category, update_position, test_task, send_email
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

        from . import NLReceiver, logger_app

        categories_have_positions = db.session.query(Category).filter(Category.turn, Category.nl_leaf).all()
        for category in categories_have_positions:
            response = NLReceiver(current_app.config["NL_GOODS"]["URL"].format(
                                                                    catalog_name=current_app.config["NL_CATALOG_MAIN"],
                                                                    category_id=category.nl_id),
                                  current_app.config["NL_GOODS"]["DATA_KEY"])

            for position in Position.gen_el_to_db(response.data):
                try:
                    db.session.add(position)
                    db.session.commit()

                    #########################
                    # This place GET characteristics to position
                    response = NLReceiver(current_app.config["NL_GOOD"]["URL"].format(
                                                                catalog_name=current_app.config["NL_CATALOG_MAIN"],
                                                                category_id=category.nl_id,
                                                                position_id=position.nl_id),
                                    current_app.config["NL_GOOD"]["DATA_KEY"])

                    characteristics = Characteristic.gen_el_to_db(position, response.data) or {}
                    for characteristic in characteristics:
                        db.session.add(characteristic)
                        try:
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()

                    #########################
                    # This place GET image to position
                    response = NLReceiver(current_app.config["NL_IMG_GOOD"]["URL"].format(goodsId=position.nl_id),
                                          current_app.config["NL_IMG_GOOD"]["DATA_KEY"])
                    import requests, hashlib, os

                    m = hashlib.md5()
                    if not response.data:
                        with open(current_app.config["DEFAULT_IMAGE_FOR_CATALOG"], "rb") as response_image:
                            response_image_content = response_image.read()
                            m.update(response_image_content)
                    else:
                        url_image = response.data["items"][0]["properties"]["Url"]
                        response_image = requests.get(
                            url_image.rsplit("&", 1)[0] + current_app.config["LOGOTYPE"])  # it is string fot URL
                        response_image_content = response_image.content
                        m.update(response_image_content)

                    hash_image = m.hexdigest()
                    image_name = hash_image + ".jpg"
                    with open(os.path.join(current_app.config["UPLOAD_FOLDER"], image_name), "wb") as f:
                        f.write(response_image_content)

                    image = Image(original_name=image_name, name=image_name, hash=hash_image)
                    position.images.append(image)
                    db.session.add(position)
                    db.session.commit()

                except Exception as e:
                    print(e)
                    db.session.rollback()
                    position_update = Position.update_position(position)
                    try:
                        db.session.add(position_update)
                        db.session.commit()
                    except Exception as e:
                        print("ERROR ___________")
                        db.session.rollback()
        # return jsonify(response.data)

    tasks = db.session.query(Task).filter(Task.name == NameTask.updating_positions.value)\
                                  .order_by(Task.timestamp_created.desc()).all()

    return render_template("backend/task_position.html", tasks=tasks)