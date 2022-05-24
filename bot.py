import discord
from discord.ext import commands
import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='?')

dataDict = { 'categories' : [],
             'values' : [],
             'rankNames' : [],
             'rankImgs' : [],
             'rankColors' : []
           }

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

# Make the bot faster at loading ranked info by:
# 1. Storing user data into a database / 
@bot.command()
async def valrank(ctx, *,username: str):
    # try:
    user = username.split("#")
    # print(user)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    response = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(user[0], user[1]), headers=headers)
    response2 = requests.get("https://valorant-api.com/v1/competitivetiers", headers=headers)

    data = response.json()
    data2 = response2.json()

    # categories = ["Rank", "Elo", "Last Match's Elo"]
    # values = [str(data['data']['currenttierpatched']), str(data['data']['ranking_in_tier']), str(data['data']['mmr_change_to_last_game'])]

    c = 0
    embed = discord.Embed()
    
    # Retrieves latest patch of data and stores it locally (this way it runs faster without having to keep requesting from server)
    if (len(dataDict['rankNames']) <= 0):

        dataDict['categories'] = ["Rank", "Elo", "Last Match's Elo"]
        dataDict['values'] = [str(data['data']['currenttierpatched']), str(data['data']['ranking_in_tier']), str(data['data']['mmr_change_to_last_game'])]

        for i in data2['data'][-1]['tiers']:
            print(i)
            if ((type(i['tierName']) == str) and (type(i['largeIcon']) == str) and (type(i['color']) == str)):
                print(i['largeIcon'])
                print(i['color'])
                dataDict['rankNames'].append(i['tierName'])
                dataDict['rankImgs'].append(i['largeIcon'])
                dataDict['rankColors'].append(i['color'])
            else:
                continue
            print("\n")

    embed.title = "{}'s Ranked Info".format(user[0])
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name=dataDict['categories'][0], value=dataDict['values'][0], inline=False)
    embed.add_field(name=dataDict['categories'][1], value=dataDict['values'][1], inline=False)
    embed.add_field(name=dataDict['categories'][2], value=dataDict['values'][2], inline=False)

    for i in range(len(dataDict['rankImgs'])):
        # print(i)
        # print(dataDict['rankNames'][i])
        # print(dataDict['rankImgs'][i])
        # print(dataDict['color'][i])
        if (dataDict['values'][0].lower() == dataDict['rankNames'][i].lower()):
            embed.color = int("0x" + str(dataDict['rankColors'][i][:6]), 16)
            embed.set_thumbnail(url=dataDict['rankImgs'][i])

    # print(data2)


    await ctx.send(embed=embed)

    # await ctx.send("Rank: " + str(data['data']['currenttierpatched']))
    # await ctx.send("Elo: " + str(data['data']['ranking_in_tier']))
    # await ctx.send("Last Match Elo: "+ str(data['data']['mmr_change_to_last_game']))
    # except:
    #     await ctx.send("ERROR")

bot.run(os.getenv("DISCORD_TOKEN"))