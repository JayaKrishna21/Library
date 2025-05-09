from flask import Flask, render_template, request, redirect, url_for






import sqlite3
def get_connection():
    return sqlite3.connect("library.db")

app = Flask(__name__)


from flask import session

app.secret_key = "your_secret_key_here"  # Required for using sessions

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

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("user_home"))
        else:
            return "<h3>Invalid credentials.</h3><a href='/user'>Back</a>"

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
    if "user_id" not in session:
        return redirect(url_for("user_login"))

    user_id = session["user_id"]
    user_name = session.get("user_name", "User")

    query = request.args.get("query")
    conn = get_connection()
    cursor = conn.cursor()

    if query:
        cursor.execute("""
            SELECT * FROM books 
            WHERE book_title LIKE ? OR author LIKE ?
        """, (f'%{query}%', f'%{query}%'))
    else:
        cursor.execute("SELECT * FROM books")
    
    books = cursor.fetchall()
    conn.close()

    return render_template("user_home.html", books=books, user_name=user_name)




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


from datetime import datetime

@app.route("/user/borrow/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    user_id = 1  # Hardcoded for now
    borrow_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Fetch stock for the book
    cursor.execute("SELECT stock FROM books WHERE book_id = ?", (book_id,))
    result = cursor.fetchone()

    if result and result[0] > 0:
        new_stock = result[0] - 1

        # Update book stock
        cursor.execute("UPDATE books SET stock = ? WHERE book_id = ?", (new_stock, book_id))

        # Delete book if stock reaches 0
        if new_stock == 0:
            cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

        # Insert borrow record
        cursor.execute("""
            INSERT INTO borrowed_books (user_id, book_id, borrow_date)
            VALUES (?, ?, ?)
        """, (user_id, book_id, borrow_date))

        conn.commit()

    conn.close()
    return redirect(url_for("user_home"))



@app.route("/user/borrowed")
def view_borrowed_books():
    user_id = 1  # Hardcoded for now

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bb.borrow_id, b.book_title, b.author, bb.borrow_date, bb.return_date
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.book_id
        WHERE bb.user_id = ?
    """, (user_id,))
    
    borrowed = cursor.fetchall()
    conn.close()

    return render_template("borrowed_books.html", borrowed=borrowed)


@app.route("/user/return/<int:borrow_id>/<int:book_id>", methods=["POST"])
def return_book(borrow_id, book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Delete the borrow record
    cursor.execute("DELETE FROM borrowed_books WHERE borrow_id = ?", (borrow_id,))

    # Increase stock if book still exists
    cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if book:
        cursor.execute("UPDATE books SET stock = stock + 1 WHERE book_id = ?", (book_id,))

    conn.commit()
    conn.close()
    return redirect(url_for("view_borrowed_books"))



from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fname = request.form["first_name"]
        lname = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match.")

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (?, ?, ?, ?)""", (fname, lname, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="Email already registered.")
        finally:
            conn.close()

        return redirect(url_for("user_login"))
    
    return render_template("signup.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("front_page"))
