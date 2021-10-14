# Handles the manipulation and indexing of the whitelist database

import os
import sqlite3

working_directory = os.getenv("working directory", os.getcwd())
whitelists_database = f"{working_directory}/UserWhitelists.db"

database_exists = os.path.exists(whitelists_database)


def write_schema_to_db():
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("""
                CREATE TABLE whitelists(
                    discordID TEXT
                )""")
        except sqlite3.Error:
            print("Failed to load schema")


if not database_exists:
    write_schema_to_db()

"""
schema:

CREATE TABLE whitelists(
    discordID TEXT PRIMARY KEY
)
"""


# Returns True if the specified ID is in the whitelists database.
def is_discord_whitelisted(discord_id: str) -> bool:
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            is_logged = cursor.execute("SELECT * FROM whitelists WHERE discordID = :dID",
                                       {"dID": discord_id}).fetchone()
        except (TypeError, sqlite3.Error):
            print(f"Failed to run whitelist check for {discord_id}")
            return False

        cursor.close()
        return is_logged is not None


# Adds a Discord id to the whitelisted database.
def whitelist_discord(discord_id: str) -> bool:
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO whitelists VALUES (:dID)",
                           {"dID": discord_id})
        except sqlite3.Error:
            return False

        return True


# Removes a Discord id from the whitelisted database.
def remove_discord_whitelist(discord_id: str) -> bool:
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM whitelists WHERE discordID=:dID",
                           {"dID": discord_id})
        except sqlite3.Error:
            return False

        return True
