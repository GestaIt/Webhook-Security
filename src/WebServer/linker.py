# Handles the creation of API keys.

from random import getrandbits

from src.SQLServer.gameManager import insert_guild, get_log_channel_id
from src.SQLServer.whitelistManager import whitelist_discord
from src.SQLServer.linkManager import create_link


# Creates an api key.
def create_api_key(guild_id: str, log_channel: str, model_log_channel) -> str:
    whitelist_discord(guild_id)
    insert_guild(guild_id, log_channel, model_log_channel)

    api_key = "%032x" % getrandbits(128)

    create_link(api_key, guild_id)

    return api_key


# Gets information on a key.
def get_api_key(key: str) -> tuple[bool, dict[str]]:
    pass
