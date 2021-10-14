import discord
import os
import json

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


async def _create_link(message_data: dict[str]) -> None:
    pass

    return


commands = {
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
                    await message_data["send message"](f"you did not specify the correct arguments!"
                                                       f"{command_data['arguments']}")
            else:
                await message_data["send message"]("you dont have the necessary permissions to run that command!!!")
        else:
            await message_data["send message"]("that command does not exist!!")

    return
