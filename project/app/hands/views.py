import json
from datetime import datetime

from celery.result import AsyncResult

from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app, jsonify
from flask_login import login_required, login_user, current_user, logout_user

from app import app, db, redis_client
from app.models import User, NameTask
from app.backend import logger_app
from app.backend.waiter import test_task

from . import hands


@hands.route("/")
def hand_main():

    # response = {"status": "success",
    #             "data": datetime.now() if datetime.now().second%2 == 0 else None}

    task_name = request.args.get("task_name")
    current_tasks = [task.decode() for task in redis_client.smembers(task_name)]

    celery_result_prefix = "celery-task-meta-{}"

    tasks = []
    for task_id in current_tasks:
        complete_task = redis_client.get(celery_result_prefix.format(task_id))

        result_task = "in_progress"
        if complete_task:
            result_task = json.loads(complete_task)

        tasks.append({"task_id": task_id, "result_task": result_task})

    response = {"status": "success",
                "data": tasks}

    return jsonify(response)


@hands.route("/ajax")
def hand_ajax():

    job = test_task.apply_async(args=[], countdown=3)

    # r = job.get()
    #
    # return make_response(r)

    return render_template("backend/test.html")