from flask import request, render_template, redirect, url_for, flash, make_response, jsonify

from app.models import db, User, TypeDealer, NameTask, Task, Category, Position, Characteristic, Image
from . import api


@api.route("/api/1.0/position/<article>")
def index(article):
    position = db.session.query(Position).filter_by(article=article).first_or_404()
    data = {
        "position_name": position.get_name,
        "position_price": position.get_price,
        "position_url_image": position.get_image,
        "position_characteristics": position.get_characteristics,
        "position_article": position.article,
    }
    resp = make_response(jsonify(data), 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"

    return resp


@api.app_errorhandler(404)
def http_404_handler(error):
    resp = make_response(jsonify({"error_msg": "Position not found"}), 404)
    resp.headers["Access-Control-Allow-Origin"] = "*"

    return resp
