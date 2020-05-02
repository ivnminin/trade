from app import db
from . import backend
from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app
from flask_login import login_required, login_user, current_user, logout_user
from app.models import User, db
from .forms import LoginForm
from app.workroom.waiter import gen_prime


@backend.route('/backend/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        try:
            job = gen_prime.apply_async(args=[100], countdown=3)
            r = job.get()
            # job = gen_prime(100)
            return make_response(', '.join(map(lambda x: str(x), r)))
        except Exception as e:
            return make_response(str(e))
            # log.error('Function send_email.apply_async has some problems, error: {}'.format(e))



    return render_template('backend/index.html')
