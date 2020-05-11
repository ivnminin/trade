import requests, zipfile, os
from celery import Celery
from celery.schedules import crontab

from app import create_app

app = create_app()
app.app_context().push()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend="redis://redis_trade:6379/0",
        broker="amqp://myuser1:mypass1@rabbitmq_trade:5672/myvhost1",
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = make_celery(app)
# celery_app.conf.beat_schedule = {
#     # Executes every Monday morning at 7:30 a.m.
#     "add-every-monday-morning": {
#         "task": "app.backend.waiter.get_xml_price",
#         "schedule": crontab(minute="*/1")
#     },
# }


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
def get_xml_price():

    response = requests.get(app.config["URL_DEALER_PRICE_ZIP"])
    file_path = "{}/tmp.zip".format(app.config["URL_DEALER_XML_FILES"])

    with open(file_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(app.config["URL_DEALER_XML_FILES"])

    os.remove(file_path)

    mgs = "Success, got price xml"
    print(mgs)

    return "{}, {}".format(mgs, app.config["URL_DEALER_XML_FILES"])

# @celery_app.task
# def send_email(id, sender, recipients):
#
#     order = db.session.query(Order).filter(Order.id == id).first()
#
#     subject = '№{}, {}'.format(order.id, order.user.full_name)
#     body = '{}\n{}\n{}\n{}'.format(subject, order.name, '-'*70, order.description)
#
#     msg = Message(subject, sender=sender, recipients=recipients)
#     msg.body = body
#     # msg.html = html_body
#     # if attachments:
#     #     for attachment in attachments:
#     #         msg.attach(*attachment)
#
#     mail.send(msg)


if __name__ == '__main__':

    pass
