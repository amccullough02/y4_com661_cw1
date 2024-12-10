from flask import Blueprint, request, make_response, jsonify
from datetime import datetime, UTC, timedelta
from bson import ObjectId
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
        jsonify({"message": "account registration successful"}), 201)


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
        jsonify({"message": "admin account registration successful"}), 201)


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
        "exp": datetime.now(UTC) + timedelta(minutes=60)},
        secret_key, algorithm="HS256")

    return make_response(jsonify({"token": token}), 200)


@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers["x-access-token"]
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "logout successful"}), 200)


@auth_bp.route("/api/v1.0/accounts", methods=["GET"])
@jwt_required
@admin_required
def get_all_accounts():
    data_to_return = []
    users_cursor = users.find()

    for user in users_cursor:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        data_to_return.append(user)

    return make_response(jsonify(data_to_return), 200)


@auth_bp.route("/api/v1.0/accounts/<string:username>", methods=["GET"])
@jwt_required
@admin_required
def get_account_by_username(username):
    user = users.find_one({"username": username})
    if user is None:
        return make_response(jsonify({"error": "user not found"}), 404)
    user.pop("password", None)
    user["_id"] = str(user["_id"])

    return make_response(jsonify(user), 200)


@auth_bp.route("/api/v1.0/accounts/<string:a_id>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_account(a_id):
    if not ObjectId.is_valid(a_id):
        return make_response(jsonify({"error": "invalid user ID"}), 400)

    if users.find_one({"_id": ObjectId(a_id)}) is None:
        return make_response(jsonify({"error": "user ID does not exist"}), 404)

    result = users.delete_one({"_id": ObjectId(a_id)})

    if result.deleted_count == 1:
        return make_response(
            jsonify({"message": "user deleted successfully"}), 200)
    else:
        return make_response(
            jsonify({"error": "deletion attempt failed"}), 500)
