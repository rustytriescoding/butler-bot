import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = "?", intents=intents)

@client.event
async def on_ready():
    print('Logged in as', client)

@client.command()
async def status(ctx):
    membersList = []
    for guild in client.guilds:
        for member in guild.members:
            print(member)
            membersList.append(member)
    print(membersList)
    print(membersList[0])
                
client.run(os.getenv("DISCORD_TOKEN"))