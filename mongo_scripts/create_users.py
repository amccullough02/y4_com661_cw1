from pymongo import MongoClient
from bcrypt import gensalt, hashpw

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.EDB_DB
users = db.users

user_list = [
    {
        "username": "starlord34",
        "forename": "Chris",
        "surname": "Pratt",
        "email": "realchrispratt@gmail.com",
        "password": b"iammario",
        "is_admin": False
    },
    {
        "username": "stargal21",
        "forename": "Zoe",
        "surname": "Saldana",
        "email": "realzoe@gmail.com",
        "password": b"iamgamora",
        "is_admin": True

    },
    {
        "username": "galaxycrusher59",
        "forename": "Robert",
        "surname": "Downey Jr.",
        "email": "youknowwhoiam@gmail.com",
        "password": b"iamironman",
        "is_admin": False
    }
]

for user in user_list:
    user["password"] = hashpw(user["password"], gensalt())
    users.insert_one(user)
