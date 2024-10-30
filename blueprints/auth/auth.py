from flask import Blueprint, request, make_response, jsonify
from datetime import datetime, UTC, timedelta
from jwt import encode
from bcrypt import checkpw
from decorators import jwt_required
from globals import db, secret_key

auth_bp = Blueprint("auth_bp", __name__)
users = db.users
blacklist = db.blacklist


@auth_bp.route("/api/v1.0/login", methods=["GET"])
def login():
    auth = request.authorization

    if not auth:
        return make_response(
            jsonify({"message": "authentication required"}), 401)

    user = users.find_one({"username": auth.username})

    if user is None:
        return make_response(
            jsonify({"message": "incorrect username"}), 401)

    if not checkpw(bytes(auth.password, "UTF-8"), user["password"]):
        return make_response(
            jsonify({"message": "incorrect password"}), 401)

    token = encode({
        "user": auth.username, "is_admin": user["is_admin"],
        "exp": datetime.now(UTC) + timedelta(minutes=30)},
        secret_key, algorithm="HS256")

    return make_response(jsonify({"token": token}), 200)


@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "logout successful"}))