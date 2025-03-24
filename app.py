def user():

    user_id = "alice@example.com"
    password = "alice"

    return user_id, password


def admin():

    user_id = "admin@example.com"
    password = "admin"

    return user_id, password

from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def front_page():
    return(render_template("create.html"))