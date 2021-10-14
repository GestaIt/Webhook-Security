# Keeps track of the clients guilds

import os
import sqlite3

working_directory = os.getenv("working directory", os.getcwd())
games_database = f"{working_directory}/GameLogs.db"

database_exists = os.path.exists(games_database)


def write_schema_to_db():
    with sqlite3.connect(games_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("""
            CREATE TABLE guildData(
                GuildID TEXT PRIMARY KEY,
                LoggingChannelID TEXT UNIQUE,
                SpamChannelID TEXT UNIQUE,
                ModelLoggingChannelID TEXT UNIQUE
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

CREATE TABLE guildData(
                GuildID TEXT PRIMARY KEY,
                LoggingChannelID TEXT UNIQUE,
                SpamChannelID TEXT UNIQUE,
                ModelLoggingChannelID TEXT UNIQUE
            )
"""


# Inserts guild information into the database.
def insert_guild(guild_id: str, logging_channel_id: str, spam_channel_id: str, model_logging_channel_id: str) -> bool:
    with sqlite3.connect(games_database) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO guildData VALUES (:gID, :lCI, :sCI, :mCI)",
                           {"gID": guild_id, "lCI": logging_channel_id, "sCI": spam_channel_id, "mCI": model_logging_channel_id})
        except sqlite3.Error:
            print(f"Failed to add guild {guild_id} to the database.")
            return False

        return True


# Gets the specified guilds log channel.
def get_log_channel_id(guild_id: str, is_logging: bool, is_spam: bool) -> tuple[bool, str]:
    with sqlite3.connect(games_database) as connection:
        cursor = connection.cursor()

        try:
            if is_logging:
                log_id = cursor.execute("SELECT LoggingChannelID FROM guildData WHERE GuildId=:gID",
                                        {"gID": guild_id}).fetchone()
            elif is_logging and is_spam:
                log_id = cursor.execute("SELECT SpamChannelID FROM guildData WHERE GuildID=:gID",
                                        {"gID": guild_id}).fetchone()
            else:
                log_id = cursor.execute("SELECT ModelLoggingChannelID FROM guildData WHERE GuildId=:gID",
                                        {"gID": guild_id}).fetchone()
        except sqlite3.Error:
            print(f"Failed to get log channel id for {guild_id}.")
            return False, ""

        if log_id:
            return True, log_id[0]

        return False, ""
