from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1/27017")
db = client.EDB_DB
bodies = db.bodies


@app.route("/api/1.0/bodies", methods=["GET"])
def query_all_stars():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))

    page_start = (page_size * (page_num - 1))

    data_to_return = []
    bodies_cursor = bodies.find().skip(page_start).limit(page_size)

    for body in bodies_cursor:
        body['_id'] = str(body['_id'])
        data_to_return.append(body)

    return make_response(jsonify(data_to_return), 200)


@app.route("/api/1.0/bodies/<string:s_id>", methods=["GET"])
def query_one_star(s_id):
    body = bodies.find_one({'_id': ObjectId(s_id)})
    if body is not None:
        body['_id'] = str(body['_id'])
    return make_response(jsonify(body), 200)


@app.route("/api/1.0/bodies", methods=["POST"])
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


@app.route("/api/1.0/bodies/<string:s_id>", methods=["PUT"])
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


@app.route("/api/1.0/bodies/<string:s_id>", methods=["DELETE"])
def remove_star(s_id):
    bodies.delete_one({"_id": ObjectId(s_id)})
    return make_response(jsonify({}), 204)


if __name__ == "__main__":
    app.run(debug=True)
