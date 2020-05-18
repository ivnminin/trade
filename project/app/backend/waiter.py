from flask_mail import Message
from celery.schedules import crontab

from app import app, celery_app
from app import mail
from app.models import db, TypeDealer, NameTask, Task, Category
from . import NLReceiver, logger_app


celery_app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    "add-every-monday-morning": {
        "task": "app.backend.waiter.update_category",
        "schedule": crontab(minute="*/1")
    },
}


@celery_app.task
def test_task():
    raise Exception("Test exception raised by celery test_task")


@celery_app.task
def update_category():

    task = Task(name=NameTask.updating_structure_of_catalog.value)
    try:

        response = NLReceiver(app.config["NL_CATEGORIES"]["URL"]
                              .format(catalog_name=app.config["NL_CATALOG_MAIN"]),
                              app.config["NL_CATEGORIES"]["DATA_KEY"])

        nl_error = response.error
        if nl_error:
            raise Exception(str(nl_error))

        root_directory = Category.query.get(1)

        if not root_directory:
            root_directory = Category(name=app.config["PRODUCT_CATALOG_ROOT_DIRECTORY"])
            db.session.add(root_directory)
            db.session.commit()

        categories = sorted(response.data.get("category", []), key=lambda x: int(x["parentId"]))
        categories_in_db = list(map(lambda x: x.nl_id, db.session.query(Category).all()[1:]))

        task_result = {"task_name": task.name, "result": {"new_category": [],
                                                          "old_category": []}}

        for category in categories:
            if int(category["id"]) not in categories_in_db:

                task_result["result"]["new_category"].append(category["name"])

                if int(category["parentId"]) == 0:
                    db.session.add(Category.gen_el_to_db(category, root_directory))
                    db.session.commit()
                else:
                    parent = db.session.query(Category).filter_by(nl_id=int(category["parentId"]),
                                                                  dealer=TypeDealer.nl_dealer.name).first()
                    db.session.add(Category.gen_el_to_db(category, parent))
                    db.session.commit()

        for category_in_db in db.session.query(Category).all()[1:]:

            if category_in_db.nl_id not in list(map(lambda x: int(x["id"]), categories)):
                task_result["result"]["old_category"].append("id: {}, name: {}".format(category_in_db.id,
                                                                                       category_in_db.name))

        task_msg_result = "TASK_NAME: {}, new_category: [{}], old_category [{}]" \
            .format(task_result["task_name"],
                    "; ".join(task_result["result"]["new_category"]),
                    "; ".join(task_result["result"]["old_category"]))

        turn_on_main_categories = db.session.query(Category).filter(Category.nl_parent_id == 0,
                                                                    Category.dealer_operation).all()

        for main_category in turn_on_main_categories:

            for category in main_category.get_subcategories():
                category.dealer_operation = True
                db.session.add(category)
                db.session.commit()

        task_msg_result = "{}, turn_on_main_categories: {}".format(task_msg_result, "success")

        task.success = True
        task.changes = True if task_result["result"]["new_category"] or \
                               task_result["result"]["old_category"] else False
        task.added = True if task_result["result"]["new_category"] else False
        task.removed = True if task_result["result"]["old_category"] else False
        task.result_msg = task_msg_result
        db.session.add(task)
        db.session.commit()

        logger_app.info(task_msg_result)

        return "success"

    except Exception as e:
        task.success = False
        task.result_msg = str(e)
        db.session.add(task)
        db.session.commit()

        logger_app.err(task.result_msg)

        return "failure"


@celery_app.task
def gen_prime(x):
    multiples = []
    results = []
    for i in range(2, x+1):
        if i not in multiples:
            results.append(i)
            for j in range(i*i, x+1, i):
                multiples.append(j)

    return results


@celery_app.task
def send_email(subject, body, sender, recipients):

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body

    # msg.html = html_body
    # if attachments:
    #     for attachment in attachments:
    #         msg.attach(*attachment)
    try:
        mail.send(msg)

        return "success"

    except Exception as e:

        logger_app.err(NameTask.sending_email.value)

        return "failure"


if __name__ == "__main__":

    pass
