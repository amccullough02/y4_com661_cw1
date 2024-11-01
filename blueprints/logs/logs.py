from flask import Blueprint, make_response, request, jsonify
from decorators import jwt_required, admin_required
from bson import ObjectId
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


@logs_bp.route("/api/v1.0/logs/user_activity", methods=["GET"])
@jwt_required
@admin_required
def user_activity():

    agr_pipeline = [
        {"$group": {"_id": "$user", "count": {"$sum": 1}}}
    ]

    agr_return = logs.aggregate(agr_pipeline)

    data_to_return = {item["_id"]: item["count"] for item in agr_return}

    return make_response(jsonify(data_to_return), 200)


@logs_bp.route("/api/v1.0/logs/<string:username>", methods=["GET"])
@jwt_required
@admin_required
def query_logs_by_user(username):
    page_num, page_size = 1, 10

    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))

    page_start = (page_size * (page_num - 1))

    user_logs = list(logs.find({"user": username}).skip(
        page_start).limit(page_size))

    if not user_logs:
        return make_response(
            jsonify({"error": "no logs contain the supplied username"}), 404)

    for log in user_logs:
        log["_id"] = str(log["_id"])

    return make_response(jsonify(user_logs), 200)


@logs_bp.route("/api/v1.0/logs/<string:l_id>", methods=["DELETE"])
@jwt_required
@admin_required
def remove_log(l_id):
    if not ObjectId.is_valid(l_id):
        return make_response(jsonify({"error": "invalid log ID"}), 400)

    if logs.find_one({"_id": ObjectId(l_id)}) is None:
        return make_response(jsonify({"error": "log ID does not exist"}), 404)

    result = logs.delete_one({"_id": ObjectId(l_id)})

    if result.deleted_count == 1:
        return make_response(
            jsonify({"message": "log deleted successfully"}), 200)
    else:
        return make_response(
            jsonify({"error": "deletion attempt failed"}), 500)


@logs_bp.route("/api/v1.0/logs", methods=["DELETE"])
@jwt_required
@admin_required
def remove_logs():
    number_of_logs = logs.count_documents({})

    if number_of_logs == 0:
        return make_response(
            jsonify({"message": "the logs collection is already empty"}), 200)

    result = logs.delete_many({})
    return make_response(
        jsonify({"message": f"{result.deleted_count} logs deleted"}), 200)
