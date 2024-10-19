from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient

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


if __name__ == "__main__":
    app.run(debug=True)
