from flask import Blueprint, make_response, request, jsonify, g
from bson import ObjectId
from decorators import jwt_required, admin_required
from datetime import datetime
from globals import db

planets_bp = Blueprint("planets_bp", __name__)
bodies = db.bodies
logs = db.logs


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets", methods=["GET"])
def query_all_planets(s_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if bodies.find_one({"_id": ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    convert_units = False

    if request.args.get("convert_units"):
        convert_units = request.args.get("convert_units").title()

    data_to_return = []
    body = bodies.find_one({"_id": ObjectId(s_id)}, {"planets": 1, "_id": 0})

    for planet in body["planets"]:
        planet["_id"] = str(planet["_id"])

        if convert_units:
            planet["mass"] *= 5.97e24
            planet["surface_temperature"] -= 273

        data_to_return.append(planet)

    return make_response(jsonify(data_to_return), 200)


@planets_bp.route("/api/v1.0/bodies/num_of_planets", methods=["GET"])
def number_of_planets():
    agr_pipeline = [
        {"$match": {"type": "star"}},
        {"$unwind": "$planets"},
        {"$match": {"planets.type": "planet"}},
        {"$count": "Number of planets"}
    ]

    agr_return = list(bodies.aggregate(agr_pipeline))

    return make_response(jsonify(agr_return), 200)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
                  methods=["GET"])
def query_one_planet(s_id, p_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if not ObjectId.is_valid(p_id):
        return make_response(jsonify({"error": "invalid planet ID"}), 400)

    if bodies.find_one({"_id": ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    if bodies.find_one({"_id": ObjectId(s_id),
                        "planets._id": ObjectId(p_id)}) is None:
        return make_response(
            jsonify({"error": "planet ID does not exist"}), 404)

    convert_units = False

    if request.args.get("convert_units"):
        convert_units = request.args.get("convert_units").title()

    body = bodies.find_one({"planets._id": ObjectId(p_id)}, {
                           "_id": 0, "planets.$": 1})

    body["planets"][0]["_id"] = str(body["planets"][0]["_id"])

    if convert_units:
        body["planets"][0]["mass"] *= 5.97e24
        body["planets"][0]["surface_temperature"] -= 273

    return make_response(jsonify(body["planets"][0]), 200)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets", methods=["POST"])
@jwt_required
def add_planet(s_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if bodies.find_one({"_id": ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    required_fields = ["name", "radius", "mass", "density",
                       "surface_temperature", "apoapsis", "periapsis",
                       "eccentricity", "orbital_period", "status",
                       "num_moons"]

    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]

    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {",".join(missing_fields)}"}), 404)

    planet_to_add = {
        "_id": ObjectId(),
        "name": request.form["name"],
        "type": "planet",
        "radius": int(request.form["radius"]),
        "mass": float(request.form["mass"]),
        "density": float(request.form["density"]),
        "surface_temperature": int(request.form["surface_temperature"]),
        "apoapsis": int(request.form["apoapsis"]),
        "periapsis": int(request.form["periapsis"]),
        "eccentricity": float(request.form["eccentricity"]),
        "orbital_period": int(request.form["orbital_period"]),
        "status": request.form["status"],
        "num_moons": int(request.form["num_moons"]),
        "contributed_by": g.current_username
    }

    result = bodies.update_one({"_id": ObjectId(s_id)},
                               {"$push": {"planets": planet_to_add}})
    if result.modified_count == 1:
        p_id = str(planet_to_add["_id"])
        r_link = f"http://127.0.0.1:5000/api/v1.0/bodies/{s_id}/planets/{p_id}"

        current_user = g.current_username
        time = datetime.now().strftime("%H:%M:%S, %m/%d/%Y")
        log = f"The user {current_user} added the planet {p_id} at {time}"
        logs.insert_one({"user": current_user, "time": time, "action": log})

        return make_response(jsonify({"url": r_link}), 201)
    else:
        return make_response(
            jsonify({"error": "failed to add planet"}), 500)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
                  methods=["PUT"])
@jwt_required
def modify_planet(s_id, p_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if not ObjectId.is_valid(p_id):
        return make_response(jsonify({"error": "invalid planet ID"}), 400)

    if bodies.find_one({"_id": ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    if bodies.find_one({"_id": ObjectId(s_id),
                        "planets._id": ObjectId(p_id)}) is None:
        return make_response(
            jsonify({"error": "planet ID does not exist"}), 404)

    body = bodies.find_one({"planets._id": ObjectId(p_id)}, {
                           "_id": 0, "planets.$": 1})
    contributor = body["planets"][0]["contributed_by"]

    if contributor != g.current_username or not g.is_admin:
        return make_response(
            jsonify({"error": "planet must be your contribution"}), 401)

    required_fields = ["name", "radius", "mass", "density",
                       "surface_temperature", "apoapsis", "periapsis",
                       "eccentricity", "orbital_period", "status",
                       "num_moons", "contributed_by"]

    missing_fields = [
        field for field in required_fields if not request.form.get(field)]

    if missing_fields:
        return make_response(
            jsonify({"error": f"missing fields: {",".join(missing_fields)}"}),
            404)

    modified_planet = {
        "planets.$.name": request.form["name"],
        "planets.$.type": "planet",
        "planets.$.radius": int(request.form["radius"]),
        "planets.$.mass": float(request.form["mass"]),
        "planets.$.density": float(request.form["density"]),
        "planets.$.surface_temperature":
        int(request.form["surface_temperature"]),
        "planets.$.apoapsis": int(request.form["apoapsis"]),
        "planets.$.periapsis": int(request.form["periapsis"]),
        "planets.$.eccentricity": float(request.form["eccentricity"]),
        "planets.$.orbital_period": int(request.form["orbital_period"]),
        "planets.$.status": request.form["status"],
        "planets.$.num_moons": int(request.form["num_moons"]),
        "planets.$.contributed_by": g.current_username
    }

    result = bodies.update_one({"planets._id": ObjectId(p_id)},
                               {"$set": modified_planet})

    if result.modified_count == 1:
        r_link = f"http://127.0.0.1:5000/api/v1.0/bodies/{s_id}/planets/{p_id}"

        current_user = g.current_username
        time = datetime.now().strftime("%H:%M:%S, %m/%d/%Y")
        log = f"The user {current_user} edited the planet {p_id} at {time}"
        logs.insert_one({"user": current_user, "time": time, "action": log})

        return make_response(jsonify({"url": r_link}), 202)
    else:
        return make_response(
            jsonify({"error": "failed to modify planet"}), 500)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
                  methods=["DELETE"])
@jwt_required
@admin_required
def remove_planet(s_id, p_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if not ObjectId.is_valid(p_id):
        return make_response(jsonify({"error": "invalid planet ID"}), 400)

    if bodies.find_one({"_id": ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    if bodies.find_one({"_id": ObjectId(s_id),
                        "planets._id": ObjectId(p_id)}) is None:
        return make_response(
            jsonify({"error": "planet ID does not exist"}), 404)

    result = bodies.update_one({"_id": ObjectId(s_id)}, {
        "$pull": {"planets": {"_id": ObjectId(p_id)}}})

    if result.matched_count == 1:

        current_user = g.current_username
        time = datetime.now().strftime("%H:%M:%S, %m/%d/%Y")
        log = f"The user {current_user} removed the planet {p_id} at {time}"
        logs.insert_one({"user": current_user, "time": time, "action": log})

        return make_response(
            jsonify({"message": "planet deleted successfully"}), 204)
    else:
        return make_response(
            jsonify({"message": "deletion attempt failed"}), 500)
