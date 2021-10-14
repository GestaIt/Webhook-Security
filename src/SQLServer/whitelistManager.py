# Handles the manipulation and indexing of the whitelist database

import os
import json
import sqlite3

working_directory = os.getenv("working directory", os.getcwd())
whitelists_database = f"{working_directory}/UserWhitelists.db"

database_exists = os.path.exists(whitelists_database)

with open(f"{working_directory}/config.json", "r") as config:
    config_json = json.load(config)
    guild_id = config_json["guild-id"]


def write_schema_to_db():
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("""
                CREATE TABLE whitelists(
                    discordID TEXT,
                    whitelisterID TEXT
                )""")
        except sqlite3.Error:
            print("Failed to load schema")


if not database_exists:
    write_schema_to_db()

"""
schema:

CREATE TABLE whitelists(
    discordID TEXT PRIMARY KEY,
    whitelisterID TEXT
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
def whitelist_discord(discord_id: str, owner_id: str) -> tuple[bool, str]:
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        if discord_id != guild_id:
            if not is_discord_whitelisted(discord_id):
                if not get_owner_guild(owner_id)[0]:
                    try:
                        cursor.execute("INSERT INTO whitelists VALUES (:dID, :oID)",
                                       {"dID": discord_id, "oID": owner_id})
                    except sqlite3.Error:
                        return False, "An error occurred."

                    return True, ""
                else:
                    return False, "You already whitelisted a guild!"
            else:
                return False, "Someone already whitelisted that guild!"
        else:
            return False, "You cannot whitelist that guild!"


# Checks what guid the specified id owns.
def get_owner_guild(owner_id: str) -> tuple[bool, str]:
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            guild_identifier = cursor.execute("SELECT discordID FROM whitelists WHERE whitelisterID=:oID",
                                              {"oID": owner_id}).fetchone()
        except sqlite3.Error:
            print(f"Failed to get the guild owned by @{owner_id}.")
            return False, ""

        if guild_identifier:
            return True, guild_identifier[0]

        return False, ""


# Gets the owner of a specified guild.
def get_guild_owner(discord_id: str) -> tuple[bool, str]:
    with sqlite3.connect(whitelists_database) as connection:
        cursor = connection.cursor()

        try:
            owner_id = cursor.execute("SELECT whitelisterID FROM whitelists WHERE discordID:gID",
                                      {"gID": discord_id}).fetchone()
        except sqlite3.Error:
            print(f"Failed to fetch the owner of guild {discord_id}")
            return False, ""

        if owner_id:
            return True, owner_id[0]

        return False, ""


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
