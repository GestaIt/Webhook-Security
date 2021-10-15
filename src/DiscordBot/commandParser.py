import json
import os

import discord

from src.DiscordBot.prompts import prompts
from src.DiscordBot.utilities import handle_prompt
from src.SQLServer.whitelistManager import whitelist_discord, is_discord_whitelisted,\
    remove_discord_whitelist, get_owner_guild
from src.SQLServer.linkManager import clear_links
from src.WebServer.linker import create_api_key

working_directory = os.getenv("working directory", os.getcwd())

with open(f"{working_directory}/config.json", "r") as config:
    config_json = json.load(config)
    prefix = config_json["prefix"]

no_mentions_allowed = discord.AllowedMentions(everyone=False, users=False, roles=False)


async def _help(message_data: dict[str]) -> None:
    commands_string = ""

    for command_name, command_details in commands.items():
        current_command_string = f"{command_name} {command_details['arguments']}" \
                                 f"\n    Description: {command_details['description']}" \
                                 f"\n    Permissions: {command_details['permission snowflake']}\n\n"

        commands_string += current_command_string

    await message_data["send message"](commands_string)

    return


async def _whitelist_guild(message_data: dict[str]) -> None:
    guild_id = message_data["arguments"][1]

    if guild_id.isdigit():
        if is_discord_whitelisted(guild_id) is not True:
            whitelist_success, error_code = whitelist_discord(guild_id, str(message_data["author"].id))

            if whitelist_success:
                await message_data["send message"]("Successfully whitelisted that guild!")
            else:
                await message_data["send message"](error_code)
        else:
            await message_data["send message"]("That guild is already whitelisted!")
    else:
        await message_data["send message"]("You did not specify a correct guild id!")

    return


async def _remove_guild(message_data: dict[str]) -> None:
    guild_id = message_data["arguments"][1]

    if guild_id.isdigit():
        if is_discord_whitelisted(guild_id) is True:
            whitelist_success = remove_discord_whitelist(guild_id)

            if whitelist_success:
                await message_data["send message"]("Successfully un-whitelisted that guild!")
            else:
                await message_data["send message"]("Failed to un-whitelist that guild, please message Gestalt.")
        else:
            await message_data["send message"]("That guild is not whitelisted!")
    else:
        await message_data["send message"]("You did not specify a correct guild id!")

    return


async def _get_whitelisted_guild(message_data: dict[str]) -> None:
    fetch_success, guild_id = get_owner_guild(str(message_data["author"].id))

    if fetch_success:
        await message_data["send message"](f"The following guilds are whitelisted by you:\n\t{guild_id}")

    return


async def _create_link(message_data: dict[str]) -> None:
    guild_id, log_channel_id, spam_channel_id, model_channel_id = \
        await handle_prompt(prompts["create-link"], message_data)

    if guild_id.isdigit() and log_channel_id.isdigit() and spam_channel_id.isdigit() and model_channel_id.isdigit():
        guild = message_data["discord_client"].get_guild(int(guild_id))

        if guild:
            channels_exist = (guild.get_channel(int(log_channel_id))) and \
                             (guild.get_channel(int(spam_channel_id))) and \
                             (guild.get_channel(int(model_channel_id)))

            if channels_exist:
                api_key = str(create_api_key(guild_id, log_channel_id, spam_channel_id, model_channel_id))

                await message_data["send message"]("Successfully generated an API Key! Check your direct messages.")
                await message_data["author"].send(f"Here is your API Key!\n\n{api_key}")
            else:
                await message_data["send message"]("One or more of your channels does not belong in your specified "
                                                   "guild!")
        else:
            await message_data["send message"]("It seems like I'm not in that specified guild, please invite me to"
                                               " your server to continue!")
    else:
        await message_data["send message"]("One of the channel id's you specified are incorrect!")

    return


async def _clear_api_keys(message_data: dict[str]) -> None:
    clear_success = clear_links()

    if clear_success:
        await message_data["send message"]("Successfully cleared all API Keys!")
    else:
        await message_data["send message"]("Failed to clear the API Keys, please message Gestalt.")

    return


commands = {
    "whitelistguild":
        {
            "function": _whitelist_guild,
            "description": "Whitelists the specified guild.",
            "arguments": "[Guild ID]",
            "argument amount": 1,
            "permission snowflake": 1
        },
    "unwhitelistguild":
        {
            "function": _remove_guild,
            "description": "Un-whitelists the specified guild.",
            "arguments": "[Guild ID]",
            "argument amount": 1,
            "permission snowflake": 2
        },
    "getwhitelistedguilds":
        {
            "function": _get_whitelisted_guild,
            "description": "Fetches all of the users whitelisted guilds.",
            "arguments": "",
            "argument amount": 0,
            "permission snowflake": 1
        },
    "createlink":
        {
            "function": _create_link,
            "description": "Creates a webhook link.",
            "arguments": "",
            "argument amount": 0,
            "permission snowflake": 1
        },
    "clearkeys":
        {
            "function": _clear_api_keys,
            "description": "Clear all of the api keys.",
            "arguments": "",
            "argument amount": 0,
            "permission snowflake": 3
        },
    "help":
        {
            "function": _help,
            "description": "Displays all of the available commands.",
            "arguments": "",
            "argument amount": 0,
            "permission snowflake": 0
        },
}


# Parses the command if it exists.
async def command_parser(message_data: dict[str]) -> None:
    if str.startswith(message_data["content"], prefix):
        if message_data["arguments"][0][len(prefix):] in commands:
            command_data = commands[message_data["arguments"][0][len(prefix):]]

            if message_data["permissions"] >= command_data["permission snowflake"]:
                if len(message_data["arguments"]) - 1 >= command_data["argument amount"]:
                    await command_data["function"](message_data)
                else:
                    await message_data["send message"](f"you did not specify the correct arguments! "
                                                       f"{command_data['arguments']}")
            else:
                await message_data["send message"]("you dont have the necessary permissions to run that command!!!")
        else:
            await message_data["send message"]("that command does not exist!!")

    return
