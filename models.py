from pymongo import MongoClient
from config import MONGO_URI,DB_NAME

client = MongoClient("mongodb://localhost:27017")
db = client["library_db"]


users = db.users
books = db.books
borrowed = db.borrowed
