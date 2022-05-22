import discord
from discord.ext import commands
import os
import requests
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
async def val(ctx, username: str):
    user = username.split("#")
  
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    response = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(user[0], user[1]), headers=headers)
    # response = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/cure/sss", headers=headers)
    print(response.json)
    await ctx.send(response.json())



bot.run(os.getenv("DISCORD_TOKEN"))