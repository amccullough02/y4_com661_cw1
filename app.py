from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1/27017")
db = client.EDB_DB
bodies = db.bodies


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
def remove_planet(s_id, p_id):
    bodies.update_one({"_id": ObjectId(s_id)}, {
                      "$pull": {"planets": {"_id": ObjectId(p_id)}}})
    return make_response(jsonify({}), 204)

# AUTH


if __name__ == "__main__":
    app.run(debug=True)
