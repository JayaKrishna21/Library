from flask import Flask, render_template, request, redirect, url_for

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

@app.route("/user/home")
def user_home():
    return render_template("user_home.html")

@app.route("/admin/home")
def admin_home():
    return render_template("admin_home.html")
