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
async def skull(ctx, userinput):
    try:
        num = int(userinput)
        if num < 1 or num > 2000:
            num = 1
            await ctx.send("Number out of range, number must be within 1-2000)")
        else:    
            msg = ''
            for x in range(num):
                msg += "💀"
            await ctx.send(msg)
    except ValueError:
        await ctx.send("Not a number!")



@bot.command()
async def valname(ctx, name: str):
    await ctx.send("Valorant username: " + name)



bot.run(os.getenv("DISCORD_TOKEN"))