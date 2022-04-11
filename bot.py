import os
import random
import discord

# Local imports
import xo

#

token = "HIER DEN TOKEN EINFÜGEN"
my_guild = "TakeItEasy"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == my_guild:
            break

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )

    # Purge XO channel if config is set to True
    if xo.xo_init_purge_channel:
        await client.get_channel(xo.xo_channel_id).purge(limit = xo.xo_purge_limit)
    # Load ranking
    await xo.load_ranking(client)

@client.event
async def on_message(message):
    # Restrict self trigger
    if message.author == client.user:
        return

    # Channel select
    if message.channel.id == xo.xo_channel_id:
        return await xo.xo_message_handler(message)

    return

client.run(token)