import discord
from discord.ext import commands
import os
import requests
import datetime
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
async def valrank(ctx, *,username: str):
    try:
        user = username.split("#")
        print(user)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        response = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(user[0], user[1]), headers=headers)

        data = response.json()      


        categories = ["Rank", "Elo", "Last Match's Elo"]
        values = [str(data['data']['currenttierpatched']), str(data['data']['ranking_in_tier']), str(data['data']['mmr_change_to_last_game'])]

        embed = discord.Embed()
        embed.title = "{} Server Status".format(ctx.guild.name)
        embed.timestamp = datetime.datetime.utcnow()
        embed.color = 0xf04e1f
        embed.set_footer(text="\u200b", icon_url=imageURL)
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name=categories[0], value=values[0], inline=False)
        embed.add_field(name=categories[1], value=values[1], inline=False)
        embed.add_field(name=categories[2], value=values[2], inline=False)
        embed.add_field(name="\u200b", value="\u200b")

        await ctx.send(embed=embed)

        # await ctx.send("Rank: " + str(data['data']['currenttierpatched']))
        # await ctx.send("Elo: " + str(data['data']['ranking_in_tier']))
        # await ctx.send("Last Match Elo: "+ str(data['data']['mmr_change_to_last_game']))
    except:
        await ctx.send("ERROR")

bot.run(os.getenv("DISCORD_TOKEN"))