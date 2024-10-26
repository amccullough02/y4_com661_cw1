from pymongo import MongoClient
from random import randint, uniform, choice
from bson.objectid import ObjectId

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.EDB_DB
bodies = db.bodies

usernames = ["starlord34", "stargal21", "galaxycrusher59", "blazingquasar02"]
spectra = ["O", "B", "A", "F", "G", "K", "M"]
statuses = ["Confirmed", "Candidate", "Disproven"]
planet_identifiers = ["b", "c", "d", "e", "f", "g", "h", "i"]

bodies_list = []


def generate_star():
    return {
        "name": "HIP" + str(randint(1, 50000)),
        "radius": randint(200000, 5000000),
        "mass": round(uniform(0.05, 3), 2),
        "density": round(uniform(1, 3), 2),
        "surface_temperature": randint(3000, 10000),
        "distance": round(uniform(5, 250), 1),
        "spectral_classification": choice(spectra),
        "apparent_magnitude": round(uniform(-1, 8), 2),
        "absolute_magnitude": round(uniform(-1, 8), 2),
        "planets": [generate_planet() for _ in range(randint(0, 9))]
    }


def generate_planet():
    return {
        "_id": ObjectId(),
        "name": "HIP" + str(randint(1, 50000)) + choice(planet_identifiers),
        "radius": randint(2000, 80000),
        "mass": round(uniform(0.1, 500), 2),
        "density": round(uniform(0.5, 7), 2),
        "surface_temperature": randint(100, 1000),
        "apoapsis": randint(4000000, 1000000000),
        "periapsis": randint(4000000, 1000000000),
        "eccentricity": round(uniform(0, 0.7), 2),
        "orbital_period": randint(1, 2000),
        "status": choice(statuses),
        "num_moons": randint(0, 20),
        "contributed_by": choice(usernames)
    }


def generate_data(num_stars):
    for i in range(num_stars):
        bodies_list.append(generate_star())


def seed_data():
    for body in bodies_list:
        bodies.insert_one(body)


if __name__ == "__main__":
    generate_data(10)
    seed_data()
    client.close()
