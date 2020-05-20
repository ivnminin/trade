from flask import Blueprint

hands = Blueprint("hands", __name__)

from . import views