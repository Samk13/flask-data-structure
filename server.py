from dataclasses import dataclass
from os import abort
from sqlite3 import Connection as SQlite3Connection, Cursor, Date
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
import os.path
from flask import Flask, request, jsonify, render_template, abort
import json

# App
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlitedb.file"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0
# SQLite configs
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQlite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foregin_keys=ON;")
        cursor.close()


with open("list_db.json") as json_file:
    data = json.load(json_file)

db = SQLAlchemy(app)
now = datetime.now()

# models
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    posts = db.relationship("BlogPost")


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(200))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@app.route("/")
def hello():
    return "Welcome!"


@app.route("/date")
def date():
    return f"date is {datetime.now()}"


# add page to show how many times it's been called


times = 0


def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir() + "/static/", filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return src
    except IOError as exc:
        return str(exc)


@app.route("/times")
def how_many_times():
    global times
    times += 1
    return render_template("index.html", times=times, x="static/test.jpg")


@app.route("/card/<int:index>")
def card_view(index):
    try:
        global data

        return render_template("card.html", data=data[index], index=index)
    except IndexError:
        return render_template("not_found.html")
        abort(404)


@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = User(
        name=data["name"],
        email=data["email"],
        address=data["address"],
        phone=data["phone"],
        posts=data["posts"],
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "user created successfully!"}), 200


@app.route("/user/descending_id", methods=["GET"])
def get_all_users_desc():
    pass


@app.route("/user/ascending_id", methods=["GET"])
def get_all_users_asc():
    pass


@app.route("/user/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    pass


@app.route("/user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    pass


# Initiate app
if __name__ == "__main__":
    app.run(debug=True)
