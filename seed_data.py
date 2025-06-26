from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["library_db"]

db.users.insert_many([
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "user1", "password": "user123", "role": "user"}
])

print("Sample users inserted.")
