import discord
import os
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as', client)

@client.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == client.user:
        return

    # testing ping feature
    if message.content == 'ping':
        await message.channel.send('Matthew das fan!')

    #ping feature comment


client.run(os.getenv("DISCORD_TOKEN"))