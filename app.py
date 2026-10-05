#!/usr/bin/env python3
"""SQLite operations for the Lab 5 user app."""

import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


DATABASE = Path(__file__).with_name("database.db")
USER_FIELDS = ("user_id", "name", "email", "phone", "address", "country")
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def connect_to_db():
    return sqlite3.connect(DATABASE)


def create_db_table():
    with connect_to_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            )"""
        )


def get_users():
    with connect_to_db() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM users").fetchall()
    return [{field: row[field] for field in USER_FIELDS} for row in rows]


def get_user_by_id(user_id):
    with connect_to_db() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    return {field: row[field] for field in USER_FIELDS} if row else {}


def insert_user(user):
    with connect_to_db() as conn:
        cursor = conn.execute(
            """INSERT INTO users (name, email, phone, address, country)
               VALUES (?, ?, ?, ?, ?)""",
            tuple(user[field] for field in USER_FIELDS[1:]),
        )
        user_id = cursor.lastrowid
    return get_user_by_id(user_id)


def update_user(user):
    with connect_to_db() as conn:
        conn.execute(
            """UPDATE users
               SET name = ?, email = ?, phone = ?, address = ?, country = ?
               WHERE user_id = ?""",
            tuple(user[field] for field in USER_FIELDS[1:]) + (user["user_id"],),
        )
    return get_user_by_id(user["user_id"])


def delete_user(user_id):
    with connect_to_db() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    return {"status": "User deleted successfully"}


@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users())


@app.route("/api/users/<user_id>", methods=["GET"])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))


@app.route("/api/users/add", methods=["POST"])
def api_add_user():
    return jsonify(insert_user(request.get_json()))


@app.route("/api/users/update", methods=["PUT"])
def api_update_user():
    return jsonify(update_user(request.get_json()))


@app.route("/api/users/delete/<user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))


if __name__ == "__main__":
    create_db_table()
    app.run()
