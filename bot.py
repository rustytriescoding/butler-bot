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
    if num < 1 or num > 4000:
        num = 1
    msg = ''
    for x in range(num):
        msg += "💀"
    await ctx.send(msg)


@bot.command()
async def valname(ctx, name: str):
    await ctx.send("Valorant username: " + name)



bot.run(os.getenv("DISCORD_TOKEN"))