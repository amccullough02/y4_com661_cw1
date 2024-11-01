from pymongo import MongoClient
from random import randint, uniform, choice
from datetime import datetime
from bson.objectid import ObjectId

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.EDB_DB
bodies = db.bodies
logs = db.logs

usernames = ["starlord34", "stargal21", "galaxycrusher59"]
spectra = ["O", "B", "A", "F", "G", "K", "M"]
statuses = ["confirmed", "candidate", "disproven"]
planet_identifiers = ["b", "c", "d", "e", "f", "g", "h", "i"]

bodies_list = []


def generate_star():
    star_name = "HIP " + str(randint(1, 50000))
    return {
        "name": star_name,
        "type": "star",
        "radius": randint(200000, 5000000),
        "mass": round(uniform(0.05, 3), 2),
        "density": round(uniform(1, 3), 2),
        "surface_temperature": randint(3000, 10000),
        "distance": round(uniform(5, 250), 1),
        "spectral_classification": choice(spectra),
        "apparent_magnitude": round(uniform(-1, 8), 2),
        "absolute_magnitude": round(uniform(-1, 8), 2),
        "planets": [generate_planet(star_name, identifier)
                    for identifier in planet_identifiers[:randint(0, 9)]]
    }


def generate_planet(star_name, identifier):
    apoapsis, periapsis = sorted((
        randint(4000000, 1000000000),
        randint(4000000, 1000000000)), reverse=True)

    eccentricity = (apoapsis - periapsis) / (apoapsis + periapsis)
    eccentricity = round(eccentricity, 2)

    username = choice(usernames)

    p_id = ObjectId()
    time = datetime.now().strftime("%H:%M:%S, %m/%d/%Y")
    log = f"The user {username} created the planet {p_id} at {time}"
    logs.insert_one({"user": username, "time": time, "action": log})

    return {
        "_id": p_id,
        "name": star_name + " " + identifier,
        "type": "planet",
        "radius": randint(2000, 80000),
        "mass": round(uniform(0.1, 500), 2),
        "density": round(uniform(0.5, 7), 2),
        "surface_temperature": randint(100, 1000),
        "apoapsis": apoapsis,
        "periapsis": periapsis,
        "eccentricity": eccentricity,
        "orbital_period": randint(1, 2000),
        "status": choice(statuses),
        "num_moons": randint(0, 20),
        "contributed_by": username
    }


def generate_data(num_stars):
    for i in range(num_stars):
        bodies_list.append(generate_star())


def seed_data():
    for body in bodies_list:
        bodies.insert_one(body)


if __name__ == "__main__":
    generate_data(150)
    seed_data()
    client.close()
