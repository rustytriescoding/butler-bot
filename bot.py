import discord
import os
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

valname = ""

@client.event
async def on_ready():
    print('Logged in as', client)

@client.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == client.user:
        return

    if message.content == 'matt1das':
        await message.channel.send('Matthew das fan!')

    if message.content == 'matt2das':
        await message.channel.send('Matthew das enemy!')    


    # Valorant Feature
    if message.content == 'valorantfeature':
        await message.channel.send('testing val')     
        valname = "cure#sss"
        await message.channel.send(valname)


client.run(os.getenv("DISCORD_TOKEN"))