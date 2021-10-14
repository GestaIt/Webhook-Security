import discord
import os
import json

from src.SQLServer.whitelistManager import whitelist_discord, is_discord_whitelisted, remove_discord_whitelist
from src.SQLServer.linkManager import create_link, get_linked_guild

working_directory = os.getenv("working directory", os.getcwd())

with open(f"{working_directory}/config.json", "r") as config:
    config_json = json.load(config)
    prefix = config_json["prefix"]

no_mentions_allowed = discord.AllowedMentions(everyone=False, users=False, roles=False)


# Sends a list of commands to the original channel
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
            whitelist_success = whitelist_discord(guild_id)

            if whitelist_success:
                await message_data["send message"]("Successfully whitelisted that guild!")
            else:
                await message_data["send message"]("Failed to whitelist that guild, please message Gestalt.")
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


async def _create_link(message_data: dict[str]) -> None:
    pass

    return


commands = {
    "whitelistguild":
        {
            "function": _whitelist_guild,
            "description": "Whitelists the specified guild.",
            "arguments": "[Guild ID]",
            "argument amount": 1,
            "permission snowflake": 3
        },
    "unwhitelistguild":
        {
            "function": _remove_guild,
            "description": "Un-whitelists the specified guild.",
            "arguments": "[Guild ID]",
            "argument amount": 1,
            "permission snowflake": 3
        },
    "createlink":
        {
            "function": _create_link,
            "description": "Creates a webhook link.",
            "arguments": "",
            "argument amount": 0,
            "permission snowflake": 1
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
                if len(message_data["arguments"])-1 >= command_data["argument amount"]:
                    await command_data["function"](message_data)
                else:
                    await message_data["send message"](f"you did not specify the correct arguments! "
                                                       f"{command_data['arguments']}")
            else:
                await message_data["send message"]("you dont have the necessary permissions to run that command!!!")
        else:
            await message_data["send message"]("that command does not exist!!")

    return
