from flask import request, make_response, jsonify
from functools import wraps
from jwt import decode
from globals import secret_key, db

blacklist = db.blacklist


def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify(
                {"message": "Token is missing"}), 401)
        bl_token = blacklist.find_one({"token": token})
        if bl_token is not None:
            return make_response(jsonify(
                {"message": "Token has expired"}), 401)
        try:
            data = decode(token, secret_key, algorithms="HS256")
        except:
            make_response(jsonify({"message": "Token is invalid"}), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper


def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = decode(token, secret_key, algorithms="HS256")
        if data["is_admin"]:
            return func(args, **kwargs)
        else:
            return make_response(jsonify(
                {'message': 'Admin access required'}), 401)
    return admin_required_wrapper
