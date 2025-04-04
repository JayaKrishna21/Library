from flask import Flask, render_template, request, redirect, url_for

import sqlite3
def get_connection():
    return sqlite3.connect("library.db")

app = Flask(__name__)

# Hardcoded credentials
def user():
    return "alice@example.com", "alice"

def admin():
    return "admin@example.com", "admin"

@app.route("/")
def front_page():
    return render_template("create.html")

@app.route("/user", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["user_id"]
        password = request.form["password"]
        expected_email, expected_pass = user()
        if email == expected_email and password == expected_pass:
            return redirect(url_for("user_home"))
        else:
            return "<h2>Invalid User Credentials</h2>"
    return render_template("user.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["user_id"]
        password = request.form["password"]
        expected_email, expected_pass = admin()
        if email == expected_email and password == expected_pass:
            return redirect(url_for("admin_home"))
        else:
            return "<h2>Invalid Admin Credentials</h2>"
    return render_template("admin.html")



@app.route("/admin/home")
def admin_home():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template("admin_home.html", books=books)

@app.route("/user/home")
def user_home():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template("user_home.html", books=books)

@app.route("/admin/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        price = request.form.get("price")
        stock = request.form.get("stock")

        # Safety check: ensure fields are filled
        if not title or not author or not price or not stock:
            return "<h3>⚠️ All fields are required!</h3><a href='/admin/home'>Back</a>"

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            return "<h3>⚠️ Price must be a number and stock an integer!</h3><a href='/admin/home'>Back</a>"

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE book_title = ? AND author = ?", (title, author))
        existing_book = cursor.fetchone()

        if existing_book:
            # Update stock and price
            updated_stock = existing_book[4] + stock
            cursor.execute(
                "UPDATE books SET stock = ?, price = ? WHERE book_id = ?",
                (updated_stock, price, existing_book[0])
            )
        else:
            # Insert new book
            cursor.execute(
                "INSERT INTO books (book_title, author, price, stock) VALUES (?, ?, ?, ?)",
                (title, author, price, stock)
            )

        conn.commit()
        conn.close()
        return redirect(url_for("admin_home"))

    return render_template("add_book.html")

@app.route("/admin/delete_book/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_home"))

@app.route("/admin/update_book/<int:book_id>", methods=["GET", "POST"])
def update_book(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])

        cursor.execute("""
            UPDATE books
            SET book_title = ?, author = ?, price = ?, stock = ?
            WHERE book_id = ?
        """, (title, author, price, stock, book_id))

        # If stock becomes 0, delete the book
        if stock == 0:
            cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

        conn.commit()
        conn.close()
        return redirect(url_for("admin_home"))

    # GET method - show current book info
    cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return render_template("update_book.html", book=book)
