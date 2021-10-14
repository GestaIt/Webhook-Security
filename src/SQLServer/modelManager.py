# Handles the manipulation and indexing of the model database

import os
import sqlite3

from src.Roblox.roblox import get_id_from_url

working_directory = os.getenv("working directory", os.getcwd())
models_database = f"{working_directory}/Models.db"

database_exists = os.path.exists(models_database)


def write_schema_to_db():
    with sqlite3.connect(models_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("""
            CREATE TABLE models(
            id TEXT,
            name TEXT,
            PRIMARY KEY (id)
            )""")

            cursor.execute("""
            CREATE TABLE user_model_blacklists(
            id TEXT,
            PRIMARY KEY (id)
            )""")

            cursor.execute("""
            CREATE TABLE group_model_blacklists(
            id TEXT,
            PRIMARY KEY (id)
            )""")
        except sqlite3.Error:
            print("Failed to load schema")

        connection.commit()
        cursor.close()


if not database_exists:
    write_schema_to_db()

"""
schema:

CREATE TABLE models(
    id TEXT,
    name TEXT
)
"""


# Returns whether or not the specified model is logged
def is_model_logged(model_id: str) -> bool:
    with sqlite3.connect(models_database) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT EXISTS(SELECT 1 FROM models WHERE id=:mID)", {"mID": model_id})

        is_logged = cursor.fetchone()[0] != 0

        cursor.close()

        return is_logged


# Returns whether or not the specified model is blacklisted
def is_model_blacklisted(creator_url: str, creator_type: str) -> bool:
    with sqlite3.connect(models_database) as connection:
        cursor = connection.cursor()
        creator_id = get_id_from_url(creator_url)

        if creator_type == "user":
            cursor.execute("SELECT EXISTS(SELECT 1 FROM user_model_blacklists WHERE id=:uID)", {"uID": creator_id})
        elif creator_type == "group":
            cursor.execute("SELECT EXISTS(SELECT 1 FROM group_model_blacklists WHERE id=:gID)", {"gID": creator_id})
        else:
            cursor.close()

            return True

        is_blacklisted = bool(cursor.fetchone()[0])
        cursor.close()

        return is_blacklisted


# Blacklists the specified model
def log_model_blacklist(creator_id: str, creator_type: str) -> bool:
    with sqlite3.connect(models_database) as connection:
        cursor = connection.cursor()

        if creator_type == "user":
            cursor.execute("INSERT INTO user_model_blacklists VALUES (:uID)", {"uID": creator_id})
        elif creator_type == "group":
            cursor.execute("INSERT INTO group_model_blacklists VALUES (:gID)", {"gID": creator_id})

        connection.commit()
        cursor.close()

        return True


# Logs the specified model
def log_model(model_id: str, model_name: str) -> None:
    with sqlite3.connect(models_database) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO models VALUES(:mID, :mName)", {"mID": model_id, "mName": model_name})

        connection.commit()
        cursor.close()
