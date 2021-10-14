# Handles the creation of API keys.

from random import getrandbits

from src.SQLServer.gameManager import insert_guild, get_log_channel_id
from src.SQLServer.linkManager import create_link, get_linked_guild


# Creates an api key.
def create_api_key(guild_id: str, log_channel: str, spam_channel: str, model_log_channel) -> str:
    insert_guild(guild_id, log_channel, spam_channel, model_log_channel)

    api_key = "%032x" % getrandbits(128)

    create_link(api_key, guild_id)

    return api_key


# Gets the guild linked to a key.
def get_key_guild(key: str) -> tuple[bool, dict[str]]:
    fetch_success, guild_id = get_linked_guild(key)

    if fetch_success:
        key_guild_information = {
            "guild": guild_id,
            "game_logging_channel": get_log_channel_id(guild_id, True, False),
            "spam_logging_channel": get_log_channel_id(guild_id, True, True),
            "model_logging_channel": get_log_channel_id(guild_id, False, False)
        }

        return True, key_guild_information

    return False, {}
