from flask import Blueprint, make_response, request, jsonify
from bson import ObjectId
from decorators import jwt_required, admin_required
from globals import db

stars_bp = Blueprint("stars_bp", __name__)
bodies = db.bodies


@stars_bp.route("/api/v1.0/bodies", methods=["GET"])
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


@stars_bp.route("/api/v1.0/bodies/<string:s_id>", methods=["GET"])
def query_one_star(s_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if bodies.find_one({'_id': ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    body = bodies.find_one({'_id': ObjectId(s_id)})
    body['_id'] = str(body['_id'])

    for planet in body.get('planets', []):
        planet['_id'] = str(planet['_id'])
    return make_response(jsonify(body), 200)


@stars_bp.route("/api/v1.0/bodies", methods=["POST"])
@jwt_required
@admin_required
def add_star():
    required_fields = ["name", "radius", "mass", "density",
                       "surface_temperature", "distance",
                       "spectral_classification", "apparent_magnitude",
                       "absolute_magnitude"]

    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]

    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {", ".join(missing_fields)}"}), 404)

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
    s_id = new_star_id.inserted_id
    r_link = f"http://127.0.0.1:5000/api/v1.0/bodies/{s_id}"

    return make_response(jsonify({"url": r_link}), 201)


@stars_bp.route("/api/v1.0/bodies/<string:s_id>", methods=["PUT"])
@jwt_required
@admin_required
def modify_star(s_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if bodies.find_one({'_id': ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    required_fields = ["name", "radius", "mass", "density",
                       "surface_temperature", "distance",
                       "spectral_classification", "apparent_magnitude",
                       "absolute_magnitude"]

    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]

    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {", ".join(missing_fields)}"}), 400)

    result = bodies.update_one(
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

    if result.modified_count == 1:
        edited_star_link = f"http://127.0.0.1:5000/api/v1.0/bodies/{s_id}"
        return make_response(jsonify({"url": edited_star_link}), 200)
    else:
        return make_response(jsonify({"error": "failed to modify star"}), 500)


@stars_bp.route("/api/v1.0/bodies/<string:s_id>", methods=["DELETE"])
@jwt_required
@admin_required
def remove_star(s_id):
    if not ObjectId.is_valid(s_id):
        return make_response(jsonify({"error": "invalid star ID"}), 400)

    if bodies.find_one({'_id': ObjectId(s_id)}) is None:
        return make_response(jsonify({"error": "star ID does not exist"}), 404)

    result = bodies.delete_one({"id": ObjectId(s_id)})

    if result.deleted_count == 1:
        return make_response(
            jsonify({"message": "star deleted successfully"}), 204)
    else:
        return make_response(
            jsonify({"error": "deletion attempt failed"}), 500)
