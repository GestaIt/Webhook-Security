import os
import json
import discord
from discord.ext import tasks
import queue
from typing import Union
from src.DiscordBot.commandParser import command_parser
from src.SQLServer.whitelistManager import is_discord_whitelisted

working_directory = os.getenv("working directory", os.getcwd())

message_queue = queue.Queue()

with open(f"{working_directory}/config.json", "r") as config:
    config_json = json.load(config)
    discord_token = config_json["discord-token"]
    prefix = config_json["prefix"]
    guild_id = int(config_json["guild-id"])
    whitelist_role_id = int(config_json["whitelist-role-id"])
    moderator_role_id = int(config_json["moderator-role-id"])
    owner_role_id = int(config_json["owner-role-id"])


# returns 2 if moderator, 1 if whitelisted, 0 if neither
async def check_permissions(member, client) -> int:
    guild = client.get_guild(guild_id)
    whitelist_role = guild.get_role(whitelist_role_id)
    moderator_role = guild.get_role(moderator_role_id)
    owner_role = guild.get_role(owner_role_id)

    if member:
        if owner_role in member.roles:
            return 3
        elif moderator_role in member.roles:
            return 2
        elif whitelist_role in member.roles:
            return 1
        else:
            return 0
    else:
        return 0


# iterates through guilds and leaves if its not whitelisted
async def check_guilds(client):
    for guild in client.guilds:
        if is_discord_whitelisted(str(guild.id)) or guild.id == 897851513920180304:
            pass
        else:
            await guild.text_channels[0].send("stop it!")
            await guild.leave()


# Start the bot
def run_bot():
    intents = discord.Intents.default()
    activity = discord.Game(name=f"{prefix}help")
    intents.members = True
    discord_client = discord.Client(intents=intents, activity=activity)

    @tasks.loop(seconds=1)
    async def log_loop():
        if not message_queue.empty():
            channel_id, *message_info = message_queue.get()
            channel = discord_client.get_channel(channel_id)

            try:
                await channel.send(**message_info[0])
            except discord.errors.HTTPException as e:
                print(e)

    @discord_client.event
    async def send_webhook_message(message: Union[str, discord.Embed], channel_id: int, embeds) -> bool:
        try:
            channel = discord_client.get_channel(channel_id)

            if embeds:
                await channel.send(embeds=message)
            else:
                await channel.send(message)
        except discord.errors.HTTPException:
            return False

        return True

    # Mark the online event
    @discord_client.event
    async def on_ready():
        print("bot is up and running!")
        await check_guilds(discord_client)
        log_loop.start()

    # Parse the users message
    @discord_client.event
    async def on_message(message):
        message_data = {
            "content": message.content,
            "author": discord_client.get_guild(guild_id).get_member(message.author.id),
            "channel": message.channel,
            "mentions": message.mentions,
            "send message": message.channel.send,
            "guild": message.guild,
            "arguments": str.split(message.content, " "),
            "discord_client": discord_client,
            "permissions": await check_permissions(discord_client.get_guild(guild_id).get_member(message.author.id),
                                                   discord_client)
        }

        await command_parser(message_data)

    # Initialize all of the channels
    @discord_client.event
    async def on_guild_join(guild):
        if is_discord_whitelisted(str(guild.id)) or guild.id == 897851513920180304:
            # setup channels and everything

            pass
        else:
            await guild.text_channels[0].send("stop it!")
            await guild.leave()

    discord_client.run(discord_token)
