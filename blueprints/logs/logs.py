from flask import Blueprint, make_response, request, jsonify, g
from bson import ObjectId
from decorators import jwt_required, admin_required
from datetime import datetime
from globals import db

logs_bp = Blueprint("logs_bp", __name__)
logs = db.logs


@logs_bp.route("/api/v1.0/logs", methods=["GET"])
@jwt_required
@admin_required
def query_all_logs():
    page_num, page_size = 1, 10

    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))

    page_start = (page_size * (page_num - 1))

    data_to_return = []
    logs_cursor = logs.find().skip(page_start).limit(page_size)

    for log in logs_cursor:
        log["_id"] = str(log["_id"])
        data_to_return.append(log)

    return make_response(jsonify(data_to_return), 200)


@logs_bp.route("/api/v1.0/user_activity", methods=["GET"])
@jwt_required
@admin_required
def user_activity():

    agr_pipeline = [
        {"$group": {"_id": "$user", "count": {"$sum": 1}}}
    ]

    agr_return = logs.aggregate(agr_pipeline)

    data_to_return = {item["_id"]: item["count"] for item in agr_return}

    return make_response(jsonify(data_to_return), 200)
    