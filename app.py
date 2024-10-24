from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
from functools import wraps
from datetime import datetime, UTC, timedelta
from jwt import encode, decode
from bcrypt import checkpw

app = Flask(__name__)
app.config["SECRET_KEY"] = "thewitchofcolchis"

client = MongoClient("mongodb://127.0.0.1/27017")

db = client.EDB_DB
bodies = db.bodies
users = db.users
blacklist = db.blacklist

# DECORATORS


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
            data = decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        except:
            make_response(jsonify({"message": "Token is invalid"}), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper


def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        if data["is_admin"]:
            return func(args, **kwargs)
        else:
            return make_response(jsonify(
                {'message': 'Admin access required'}), 401)
    return admin_required_wrapper

# STARS


@app.route("/api/v1.0/bodies", methods=["GET"])
def query_all_stars():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))

    page_start = (page_size * (page_num - 1))

    data_to_return = []
    bodies_cursor = bodies.find().skip(page_start).limit(page_size)

    for star in bodies_cursor:
        star['_id'] = str(star['_id'])
        for planet in star.get('planets', []):
            planet['_id'] = str(planet['_id'])
        data_to_return.append(star)

    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/bodies/<string:s_id>", methods=["GET"])
def query_one_star(s_id):
    body = bodies.find_one({'_id': ObjectId(s_id)})
    if body is not None:
        body['_id'] = str(body['_id'])
        for planet in body.get('planets', []):
            planet['_id'] = str(planet['_id'])
    return make_response(jsonify(body), 200)


@app.route("/api/v1.0/bodies", methods=["POST"])
@jwt_required
@admin_required
def add_star():
    new_star = {
        "name": request.form["name"],
        "radius": request.form["radius"],
        "mass": request.form["mass"],
        "density": request.form["density"],
        "surface_temperature": request.form["surface_temperature"],
        "distance": request.form["distance"],
        "spectral_classification": request.form["spectral_classification"],
        "apparent_magnitude": request.form["apparent_magnitude"],
        "absolute_magnitude": request.form["absolute_magnitude"],
        "planets": []
    }
    new_star_id = bodies.insert_one(new_star)
    new_star_link = "http://127.0.0.1:5000/api/v1.0/bodies/" + \
        str(new_star_id.inserted_id)
    return make_response(jsonify({"url": new_star_link}), 201)


@app.route("/api/v1.0/bodies/<string:s_id>", methods=["PUT"])
@jwt_required
@admin_required
def modify_star(s_id):
    bodies.update_one(
        {"_id": ObjectId(s_id)}, {"$set": {
            "name": request.form["name"],
            "radius": request.form["radius"],
            "mass": request.form["mass"],
            "density": request.form["density"],
            "surface_temperature": request.form["surface_temperature"],
            "distance": request.form["distance"],
            "spectral_classification": request.form["spectral_classification"],
            "apparent_magnitude": request.form["apparent_magnitude"],
            "absolute_magnitude": request.form["absolute_magnitude"]
        }})
    edited_star_link = "http://127.0.0.1:5000/api/v1.0/bodies/" + s_id
    return make_response(jsonify({"url": edited_star_link}), 200)


@app.route("/api/v1.0/bodies/<string:s_id>", methods=["DELETE"])
@jwt_required
@admin_required
def remove_star(s_id):
    bodies.delete_one({"_id": ObjectId(s_id)})
    return make_response(jsonify({}), 204)  # TODO: {} not returned

# PLANETS


@app.route("/api/v1.0/bodies/<string:s_id>/planets", methods=["GET"])
def query_all_planets(s_id):
    data_to_return = []
    body = bodies.find_one(
        {"_id": ObjectId(s_id)},
        {"planets": 1, "_id": 0})
    for planet in body["planets"]:
        planet["_id"] = str(planet["_id"])
        data_to_return.append(planet)
    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
           methods=["GET"])
def query_one_planet(s_id, p_id):
    body = bodies.find_one(
        {"planets._id": ObjectId(p_id)},
        {"_id": 0, "planets.$": 1})
    body["planets"][0]["_id"] = str(body["planets"][0]["_id"])
    return make_response(jsonify(body["planets"][0]), 200)


@app.route("/api/v1.0/bodies/<string:s_id>/planets", methods=["POST"])
@jwt_required
def add_planet(s_id):
    planet_to_add = {
        "_id": ObjectId(),
        "name": request.form["name"],
        "radius": request.form["radius"],
        "mass": request.form["mass"],
        "density": request.form["density"],
        "surface_temperature": request.form["surface_temperature"],
        "apoapsis": request.form["apoapsis"],
        "periapsis": request.form["periapsis"],
        "eccentricity": request.form["eccentricity"],
        "orbital_period": request.form["orbital_period"],
        "status": request.form["status"],
        "num_moons": request.form["num_moons"],
        "contributed_by": request.form["contributed_by"]
    }
    bodies.update_one({"_id": ObjectId(s_id)}, {"$push":
                                                {"planets": planet_to_add}})
    new_planet_link = "http://127.0.0.1:5000/api/v1.0/bodies/" + \
        s_id + "/planets/" + str(planet_to_add["_id"])
    return make_response(jsonify({"url": new_planet_link}), 201)


@app.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
           methods=["PUT"])
@jwt_required
def modify_planet(s_id, p_id):
    modified_planet = {
        "planets.$.name": request.form["name"],
        "planets.$.radius": request.form["radius"],
        "planets.$.mass": request.form["mass"],
        "planets.$.density": request.form["density"],
        "planets.$.surface_temperature": request.form["surface_temperature"],
        "planets.$.apoapsis": request.form["apoapsis"],
        "planets.$.periapsis": request.form["periapsis"],
        "planets.$.eccentricity": request.form["eccentricity"],
        "planets.$.orbital_period": request.form["orbital_period"],
        "planets.$.status": request.form["status"],
        "planets.$.num_moons": request.form["num_moons"],
        "planets.$.contributed_by": request.form["contributed_by"]
    }
    bodies.update_one({"planets._id": ObjectId(p_id)},
                      {"$set": modified_planet})
    modified_planet_url = "http://127.0.0.1:5000/api/v1.0/bodies/" + \
        s_id + "/planets/" + p_id
    return make_response(jsonify({"url": modified_planet_url}), 200)


@app.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
           methods=["DELETE"])
@jwt_required
@admin_required
def remove_planet(s_id, p_id):
    bodies.update_one({"_id": ObjectId(s_id)}, {
                      "$pull": {"planets": {"_id": ObjectId(p_id)}}})
    return make_response(jsonify({}), 204)

# AUTH


@app.route("/api/v1.0/login", methods=["GET"])
def login():
    auth = request.authorization
    if auth:
        user = users.find_one({"username": auth.username})
        if user is not None:
            if checkpw(bytes(auth.password, "UTF-8"), user["password"]):
                token = encode({
                    "user": auth.username,
                    "is_admin": user["is_admin"],
                    "exp": datetime.now(UTC) + timedelta(minutes=30)},
                    app.config["SECRET_KEY"],
                    algorithm="HS256")
                return make_response(jsonify({"token": token}), 200)
            else:
                return make_response(jsonify({
                    "message": "Incorrect password"
                }), 401)
        else:
            return make_response(jsonify({
                "message": "Incorrect username"
            }),  401)
    return make_response(jsonify({
        "message": "Authentication required"
    }), 401)


@app.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "Logout successful"}))


if __name__ == "__main__":
    app.run(debug=True)
