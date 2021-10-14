# Helpful functions for the discord bot

import discord
import requests
from discord.ext.commands import context
from typing import Any
import src.DiscordBot.discordBot
from src.SQLServer.modelManager import is_model_logged, log_model
from src.SQLServer.gameManager import get_log_channel_id


# Used by handle_prompt, ensures a sent message is a proper response to the prompt sent
def prompt_check(message_data: dict[str, Any], ctx: context) -> bool:
    return ctx.author.id == message_data["author"].id and ctx.channel == message_data["channel"]


# Returns the appropriate channel(s) for a given place
def get_logging_channels(guild_id: str) -> tuple[bool, str]:
    retrieve_success, log_id = get_log_channel_id(guild_id, True)

    if retrieve_success:
        return True, log_id

    return False, ""


# Takes a specified list of questions and prompts them to the user, returns the user's answers to the questions
async def handle_prompt(prompts: list[str], message_data: dict[str, Any]) -> list[str]:
    responses = []

    for prompt in prompts:
        await message_data["send message"](prompt)
        response_message_object = await message_data["discord_client"].wait_for("message", check=lambda ctx: prompt_check(message_data, ctx))
        responses.append(response_message_object.content)

    return responses


# Adds a game log message to the queue
def queue_game_logging_message(guild_id: str, place_details: dict[str, Any], job_id: str) -> bool:
    embed_success, message_dictionary = generate_place_logging_dictionary(place_details, job_id)

    if embed_success:
        channels = get_logging_channels(guild_id)

        for channel_id in channels:
            src.DiscordBot.discordBot.message_queue.put([channel_id, message_dictionary])

        return True
    else:
        print(f"Failed generating log embeds for {place_details['name']}")

    return False


# Adds a model log message to the queue
def queue_model_logging_message(guild_id: str, model_info: dict) -> bool:
    channel_id = get_logging_channels(guild_id)

    download_response = requests.get(f"https://assetdelivery.roblox.com/v1/assetId/{model_info['id']}")
    download_json = download_response.json()

    if "location" not in download_json.keys():
        return False

    download_link = download_json["location"]
    embed_success, message_dictionary = generate_model_logging_dictionary(model_info, download_link)

    if embed_success and not is_model_logged(model_info["id"]):
        log_model(model_info["id"], model_info["name"])

        src.DiscordBot.discordBot.message_queue.put([channel_id, message_dictionary])
        return True

    return False


# Adds a script log message to the queue
def queue_script_logging_message(guild_id: str, place_details: dict[str, Any], job_id: str, script_source: str, roblox_user_id: int, roblox_username: str) -> bool:
    channel_id = get_logging_channels(guild_id)
    embed_success, message_dictionary = generate_script_logging_dictionary(place_details, job_id, script_source, roblox_user_id, roblox_username)

    if embed_success:
        src.DiscordBot.discordBot.message_queue.put([channel_id, message_dictionary])
        return True
    else:
        print(f"Failed generating script log embeds for {place_details['name']}")

    return False


# Creates and returns the embeds for a place log message
def generate_place_logging_dictionary(game_data: dict[str, Any], job_id: str) -> tuple[bool, Any]:
    try:
        embed = discord.Embed(title=game_data["name"], colour=discord.Colour(0xdf5dff),
                              url=f"https://www.roblox.com/games/{str(game_data['rootPlaceId'])}/")

        embed.set_image(
            url=f"https://www.roblox.com/asset-thumbnail/image?assetId={str(game_data['rootPlaceId'])}&width=768&height=432&format=png")
        embed.set_author(name="Project Typhon - HTTP")
        embed.set_footer(text="made by yours truly")

        embed.add_field(name="Players", value="{:,}".format(game_data["playing"]), inline=True)
        embed.add_field(name="Visits", value="{:,}".format(game_data["visits"]), inline=True)
        embed.add_field(name="Max Players", value=game_data["maxPlayers"], inline=True)
        embed.add_field(name="Place ID", value=game_data["rootPlaceId"], inline=True)
        embed.add_field(name="Game URL", value=f"https://www.roblox.com/games/{str(game_data['rootPlaceId'])}/",
                        inline=True)
        embed.add_field(name="Job ID", value=job_id, inline=True)

        return True, {"embed": embed}
    except (discord.errors.HTTPException, KeyError):
        print(f"oh no! {game_data['name']} had an error!")
        return False, []


# Creates and returns the embeds for a model log message
def generate_model_logging_dictionary(model_info: dict, download_link: str) -> tuple[bool, dict]:
    embed = discord.Embed(title="Typhoon Model Logger", colour=discord.Colour(0xffe485))

    embed.set_thumbnail(url=model_info["thumbnail_url"])

    embed.add_field(name="Name", value=model_info["name"], inline=False)
    embed.add_field(name="Description", value=model_info["description"][:100] if model_info["description"] != "" else "None", inline=False)
    embed.add_field(name="Creator", value=f"[{model_info['creator_name']}]({model_info['creator_url']})")
    embed.add_field(name="Download Link", value=download_link, inline=False)
    embed.add_field(name="Asset Link", value=model_info["asset_url"], inline=False)

    return True, {"embed": embed}


# Creates and returns the embeds for a script log message
def generate_script_logging_dictionary(game_data: dict[str, Any], job_id: str, script_source: str, roblox_user_id: int, roblox_username: str) -> tuple[bool, Any]:
    # The threshold for whether or not the script source is included in the embed or a separate file is 500
    requires_file_for_script = len(script_source) >= 500

    try:
        embed = discord.Embed(title="typhon", colour=discord.Colour(0x9013fe), description="script logged!\n\n** **")

        embed.set_image(url=f"https://www.roblox.com/asset-thumbnail/image?assetId={str(game_data['rootPlaceId'])}&width=768&height=432&format=png")
        embed.set_footer(text="typhon script logger")

        embed.add_field(name="game", value=f"https://www.roblox.com/games/{str(game_data['rootPlaceId'])}/", inline=True)
        embed.add_field(name="executor name", value=roblox_username, inline=True)
        embed.add_field(name="executor id", value=str(roblox_user_id), inline=True)
        if not requires_file_for_script:
            embed.add_field(name="script source", value=f"```lua\n{script_source}\n```", inline=True)
        else:
            embed.add_field(name="script source", value="see attached file", inline=True)
            with open(r"source.lua", "w") as script_file:
                script_file.write(f"--Script generated courtesy of Project Typhon\n\n {script_source}")

        embed.add_field(name="job id", value=job_id, inline=True)

        if not requires_file_for_script:
            dictionary = {"embed": embed}
        else:
            dictionary = {"embed": embed, "file": discord.File("source.lua")}

        return True, dictionary
    except (discord.errors.HTTPException, KeyError):
        print(f"oh no! {game_data['name']} had an error!")
        return False, []
