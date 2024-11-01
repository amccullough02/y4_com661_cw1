from flask import Blueprint, request, make_response, jsonify
from datetime import datetime, UTC, timedelta
from jwt import encode
from bcrypt import checkpw, gensalt, hashpw
from decorators import jwt_required, admin_required
from globals import db, secret_key

auth_bp = Blueprint("auth_bp", __name__)
users = db.users
blacklist = db.blacklist


@auth_bp.route("/api/v1.0/register", methods=["POST"])
def register():
    required_fields = ["username", "surname", "forename", "email", "password"]

    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]

    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {",".join(missing_fields)}"}), 404)

    username = request.form["username"]
    email = request.form["email"]
    forename = request.form["forename"]
    surname = request.form["surname"]
    password = request.form["password"].encode("utf-8")

    if users.find_one({"username": username}):
        return make_response(
            jsonify({"error": "username already exists"}), 400)

    if users.find_one({"email": email}):
        return make_response(
            jsonify({"error": "email already exists"}), 400)

    password = hashpw(password, gensalt())

    user_to_add = {
        "username": username,
        "email": email,
        "forename": forename,
        "surname": surname,
        "password": password,
        "is_admin": False
    }

    users.insert_one(user_to_add)

    return make_response(
        jsonify({"message": "account registration successful"}), 200)


@auth_bp.route("/api/v1.0/register_admin", methods=["POST"])
@jwt_required
@admin_required
def register_admin():
    required_fields = ["username", "surname", "forename", "email", "password"]

    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]

    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {",".join(missing_fields)}"}), 404)

    username = request.form["username"]
    email = request.form["email"]
    forename = request.form["forename"]
    surname = request.form["surname"]
    password = request.form["password"].encode("utf-8")

    if users.find_one({"username": username}):
        return make_response(
            jsonify({"error": "username already exists"}), 400)

    if users.find_one({"email": email}):
        return make_response(
            jsonify({"error": "email already exists"}), 400)

    password = hashpw(password, gensalt())

    user_to_add = {
        "username": username,
        "email": email,
        "forename": forename,
        "surname": surname,
        "password": password,
        "is_admin": True
    }

    users.insert_one(user_to_add)

    return make_response(
        jsonify({"message": "admin account registration successful"}), 200)


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
    token = request.headers["x-access-token"]
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "logout successful"}), 200)
