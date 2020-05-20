from datetime import datetime

from celery.result import AsyncResult

from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app, jsonify
from flask_login import login_required, login_user, current_user, logout_user

from app import app, db
from app.models import User, NameTask
from app.backend import logger_app
from app.backend.waiter import test_task

from . import hands


@hands.route("/")
def hand_main():

    # response = {"status": "success",
    #             "data": datetime.now() if datetime.now().second%2 == 0 else None}
    tax_id = request.args.get("task_name")
    response = {"status": "success",
                "data": tax_id}

    return jsonify(response)


@hands.route("/ajax")
def hand_ajax():

    job = test_task.apply_async(args=[], countdown=3)

    r = job.get()

    return make_response(r)

    # return render_template("backend/test.html")