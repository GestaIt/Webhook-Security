# Keeps track of all of the special links

import os
import sqlite3

working_directory = os.getenv("working directory", os.getcwd())
links_database = f"{working_directory}/Links.db"

database_exists = os.path.exists(links_database)


def write_schema_to_db():
    with sqlite3.connect(links_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("""
            CREATE TABLE links(
                Link TEXT PRIMARY KEY,
                GuildID TEXT UNIQUE
            )
            """)
        except sqlite3.Error:
            print("Failed to load schema")

        connection.commit()
        cursor.close()


if not database_exists:
    write_schema_to_db()

"""
schema:

CREATE TABLE links(
                  Link TEXT PRIMARY KEY,
                  GuildID TEXT UNIQUE
                  )
"""


# Creates a new link and inserts it into the database.
def create_link(link: str, linked_guild: str) -> bool:
    with sqlite3.connect(links_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO links VALUES (:l, :lG)",
                           {"l": link, "lG": linked_guild})
        except sqlite3.Error:
            print("Failed to add a new link to the database.")
            return False

        return True


# Deletes an api link.
def delete_link(link: str) -> bool:
    with sqlite3.connect(links_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM links WHERE Link=:l",
                           {"l": link})
        except sqlite3.Error:
            print(f"Failed to delete link {link}.")
            return False

        return True


# Clears the link database.
def clear_links() -> bool:
    with sqlite3.connect(links_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM links")
        except sqlite3.Error:
            print("Failed to clear links.")
            return False

        return True


# Gets the linked guild for the specified link.
def get_linked_guild(link: str) -> tuple[bool, str]:
    with sqlite3.connect(links_database) as connection:
        cursor = connection.cursor()

        try:
            guild_id = cursor.execute("SELECT GuildID FROM links WHERE Link=:l",
                                      {"l": link}).fetchone()
        except sqlite3.Error:
            print(f"Failed to get the linked guild for the link {link}.")
            return False, ""

        return True, guild_id
