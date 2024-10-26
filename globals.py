from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1/27017")
db = client.EDB_DB
secret_key = "thewitchofcolchis"
