from app import db
from . import frontend
from flask import request, render_template, redirect, url_for, flash, make_response, session, current_app
from flask_login import login_required, login_user, current_user, logout_user
from app.models import User


@frontend.route('/')
def index():
    return render_template('frontend/index.html')
