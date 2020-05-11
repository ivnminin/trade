from app import db
from . import backend
from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app
from flask_login import login_required, login_user, current_user, logout_user
from app.models import db, User, TypeDealer, Category
from .forms import LoginForm
from .waiter import gen_prime, get_xml_price
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
            # job = get_xml_price.apply_async(args=[], countdown=3)
            # r = job.get()

            task_name = "UPDATING STRUCTURE OF CATALOG"

            response = NLReceiver(current_app.config["NL_CATEGORIES"]["URL"]
                                  .format(catalog_name=current_app.config["NL_CATALOG_MAIN"]),
                                  current_app.config["NL_CATEGORIES"]["DATA_KEY"])

            nl_error = response.error
            if nl_error:
                raise Exception(str(nl_error))

            root_directory = Category.query.get(1)

            if not root_directory:
                root_directory = Category(name=current_app.config['PRODUCT_CATALOG_ROOT_DIRECTORY'])
                db.session.add(root_directory)
                db.session.commit()

            categories = sorted(response.data.get("category", []), key=lambda x: int(x["parentId"]))
            categories_in_db = list(map(lambda x: x.nl_id, db.session.query(Category).all()[1:]))

            task_result = {"task_name": task_name, "result": {"new_category": [],
                                                              "old_category": []}}

            for category in categories:
                if int(category["id"]) not in categories_in_db:

                    task_result["result"]["new_category"].append(category["name"])

                    if int(category["parentId"]) == 0:
                        db.session.add(Category.gen_el_to_db(category, root_directory))
                        db.session.commit()
                    else:
                        parent = db.session.query(Category).query.filter_by(nl_id=int(category["parentId"]),
                                                          dealer=TypeDealer.nl_dealer.name).first()
                        db.session.add(Category.gen_el_to_db(category, parent))
                        db.session.commit()

            for category_in_db in db.session.query(Category).all()[1:]:

                if category_in_db.nl_id not in list(map(lambda x: int(x["id"]), categories)):
                    task_result["result"]["old_category"].append("id: {}, name: {}".format(category_in_db.id,
                                                                                           category_in_db.name))

            task_msg_result = "TASK_NAME: {}, new_category: [{}], old_category [{}]"\
                              .format(task_result["task_name"],
                                      "; ".join(task_result["result"]["new_category"]),
                                      "; ".join(task_result["result"]["old_category"]))

            turn_on_main_categories = db.session.query(Category).filter(Category.nl_parent_id == 0, Category.dealer_operation).all()

            for main_category in turn_on_main_categories:

                for category_ in main_category.get_subcategories():
                    category_.dealer_operation = True
                    db.session.add(category_)
                    db.session.commit()

            task_msg_result = "{}, turn_on_main_categories: {}".format(task_msg_result, "success")

            logger_dealer_nl.info(task_msg_result)

            return make_response(task_msg_result)

        except Exception as e:
            print(str(e))
            # task.group.has_error = True
            # db.session.add(task)
            # db.session.commit()
            # logger_dealer_nl.error('INSTALL CATEGORIES Failed {}'.format(str(e)))

        #     return make_response(json.dumps(response.data))
        # except Exception as e:
        #     return make_response(str(e))
        #     log.error("Function send_email.apply_async has some problems, error: {}".format(e))

    return render_template("backend/index.html")


@backend.route("/backend/category", methods=["GET", "POST"])
def category():

    categories = db.session.query(Category).all()

    return render_template("backend/category.html", categories=categories)