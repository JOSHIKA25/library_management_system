# routes.py - Flask Blueprint with complete features for Library Management System

from flask import Blueprint, render_template, request, redirect, url_for, session
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from models import users, books, borrowed

routes = Blueprint('routes', __name__)

def init_db():
    # Only initialize if collections are empty
    if users.count_documents({}) == 0:
        # Add sample users
        sample_users = [
            {"username": "admin", "password": "admin123", "role": "admin"},
            {"username": "john", "password": "john123", "role": "user"},
            {"username": "emma", "password": "emma123", "role": "user"},
            {"username": "michael", "password": "michael123", "role": "user"},
            {"username": "sarah", "password": "sarah123", "role": "user"},
            {"username": "david", "password": "david123", "role": "user"},
            {"username": "lisa", "password": "lisa123", "role": "user"},
            {"username": "james", "password": "james123", "role": "user"},
            {"username": "anna", "password": "anna123", "role": "user"},
            {"username": "peter", "password": "peter123", "role": "user"},
            {"username": "mary", "password": "mary123", "role": "user"}
        ]
        users.insert_many(sample_users)
    
    if books.count_documents({}) == 0:
        # Add sample books
        sample_books = [
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "available": True},
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "available": True},
            {"title": "1984", "author": "George Orwell", "available": True},
            {"title": "Pride and Prejudice", "author": "Jane Austen", "available": True},
            {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "available": True},
            {"title": "Lord of the Flies", "author": "William Golding", "available": True},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "available": True},
            {"title": "Fahrenheit 451", "author": "Ray Bradbury", "available": True},
            {"title": "The Alchemist", "author": "Paulo Coelho", "available": True},
            {"title": "The Little Prince", "author": "Antoine de Saint-Exupéry", "available": True}
        ]
        books.insert_many(sample_books)

# Initialize database with sample data
init_db()

@routes.route("/")
def home():
    return redirect(url_for("routes.login"))

@routes.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        user = users.find_one({"username": username, "password": password, "role": role})
        if user:
            session["username"] = username
            session["role"] = role
            if role == "admin":
                return redirect(url_for("routes.admin_dashboard"))
            else:
                return redirect(url_for("routes.user_dashboard"))
        else:
            error = "Invalid username, password, or role."
    return render_template("login.html", error=error)

@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))

# ADMIN ROUTES
@routes.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))
    return render_template("admin_dashboard.html")

@routes.route("/add_book_page")
def add_book_page():
    return render_template("add_book.html")

@routes.route("/add_book", methods=["POST"])
def add_book():
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))
    title = request.form["title"]
    author = request.form["author"]
    books.insert_one({"title": title, "author": author, "available": True})
    return redirect(url_for("routes.view_books"))

@routes.route("/view_books")
def view_books():
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))
    all_books = list(books.find())
    return render_template("view_books.html", books=all_books)

@routes.route("/manage_borrowed_books")
def manage_borrowed_books():
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))

    borrowed_records = list(borrowed.find())
    borrowed_list = []
    for record in borrowed_records:
        book = books.find_one({"_id": ObjectId(record["book_id"])})
        borrowed_list.append({
            "_id": str(record["_id"]),
            "book_title": book["title"] if book else "Unknown",
            "username": record["username"],
            "borrowed_date": record["borrowed_date"],
            "return_date": record["return_date"],
            "returned": record.get("returned", False)
        })

    return render_template("manage_borrowed.html", borrowed=borrowed_list)

@routes.route("/return_book/<borrow_id>")
def return_book(borrow_id):
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))

    record = borrowed.find_one({"_id": ObjectId(borrow_id)})
    if record:
        books.update_one({"_id": ObjectId(record["book_id"])} , {"$set": {"available": True}})
        borrowed.update_one({"_id": ObjectId(borrow_id)}, {"$set": {"returned": True}})

    return redirect(url_for("routes.manage_borrowed_books"))

@routes.route("/edit_book/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))
    
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        books.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"title": title, "author": author}}
        )
        return redirect(url_for("routes.view_books"))
    
    book = books.find_one({"_id": ObjectId(book_id)})
    return render_template("edit_book.html", book=book)

@routes.route("/delete_book/<book_id>")
def delete_book(book_id):
    if session.get("role") != "admin":
        return redirect(url_for("routes.login"))
    
    books.delete_one({"_id": ObjectId(book_id)})
    return redirect(url_for("routes.view_books"))

@routes.route('/admin/profile')
def admin_profile():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('routes.login'))
    
    user = users.find_one({"username": session['username']})
    if not user:
        return redirect(url_for('routes.login'))
        
    total_books = books.count_documents({})
    available_books = books.count_documents({"available": True})
    borrowed_books = books.count_documents({"available": False})
    
    return render_template('admin_profile.html', 
                         user=user,
                         total_books=total_books,
                         available_books=available_books,
                         borrowed_books=borrowed_books)

# USER ROUTES
@routes.route("/user")
def user_dashboard():
    if session.get("role") != "user":
        return redirect(url_for("routes.login"))
    books_available = list(books.find({"available": True}))
    return render_template("user_dashboard.html", books=books_available)

@routes.route("/borrow/<book_id>")
def borrow(book_id):
    if session.get("role") != "user":
        return redirect(url_for("routes.login"))

    book = books.find_one({"_id": ObjectId(book_id)})
    if not book or not book.get("available"):
        return "Book not available"

    books.update_one({"_id": ObjectId(book_id)}, {"$set": {"available": False}})

    borrowed.insert_one({
        "book_id": str(book["_id"]),
        "book_title": book["title"],
        "username": session["username"],
        "borrowed_date": datetime.now().strftime("%Y-%m-%d"),
        "return_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "returned": False
    })

    return redirect(url_for("routes.view_borrowed_books"))

@routes.route("/view_borrowed_books")
def view_borrowed_books():
    if session.get("role") != "user":
        return redirect(url_for("routes.login"))

    user_records = list(borrowed.find({"username": session["username"], "returned": False}))
    return render_template("view_borrowed.html", borrowed_books=user_records)

@routes.route("/profile")
def profile():
    if session.get("role") != "user":
        return redirect(url_for("routes.login"))
    user = users.find_one({"username": session["username"]})
    return render_template("profile.html", user=user)

@routes.route("/available_books")
def available_books():
    if not session.get("username"):
        return redirect(url_for("routes.login"))
    
    available_books = list(books.find({"available": True}))
    is_admin = session.get("role") == "admin"
    return render_template("available_books.html", books=available_books, is_admin=is_admin)
