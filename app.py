#!/usr/bin/env python3
"""EECE 435L Lab 5: Flask user app — Jad El Harkae."""

import sqlite3
from contextlib import closing
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
    with closing(connect_to_db()) as conn, conn:
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
    try:
        with closing(connect_to_db()) as conn, conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM users").fetchall()
        return [{field: row[field] for field in USER_FIELDS} for row in rows]
    except sqlite3.Error:
        return []


def get_user_by_id(user_id):
    try:
        with closing(connect_to_db()) as conn, conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return {field: row[field] for field in USER_FIELDS} if row else {}
    except sqlite3.Error:
        return {}


def insert_user(user):
    try:
        with closing(connect_to_db()) as conn, conn:
            cursor = conn.execute(
                """INSERT INTO users (name, email, phone, address, country)
                   VALUES (?, ?, ?, ?, ?)""",
                tuple(user[field] for field in USER_FIELDS[1:]),
            )
            user_id = cursor.lastrowid
        return get_user_by_id(user_id)
    except (sqlite3.Error, KeyError, TypeError):
        return {}


def update_user(user):
    try:
        with closing(connect_to_db()) as conn, conn:
            conn.execute(
                """UPDATE users
                   SET name = ?, email = ?, phone = ?, address = ?, country = ?
                   WHERE user_id = ?""",
                tuple(user[field] for field in USER_FIELDS[1:]) + (user["user_id"],),
            )
        return get_user_by_id(user["user_id"])
    except (sqlite3.Error, KeyError, TypeError):
        return {}


def delete_user(user_id):
    try:
        with closing(connect_to_db()) as conn, conn:
            conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        return {"status": "User deleted successfully"}
    except sqlite3.Error:
        return {"status": "Cannot delete user"}


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
