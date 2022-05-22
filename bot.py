import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


bot = commands.Bot(command_prefix='?')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def add(ctx, left: int, right: int):
    await ctx.send(left + right)

@bot.command()
async def skull(ctx, num: int):
    msg = ''
    for x in range(num):
        msg += "💀"
    await ctx.send(msg)


@bot.command()
async def valname(ctx, name: str):
    await ctx.send("Valorant username: " + name)



bot.run(os.getenv("DISCORD_TOKEN"))