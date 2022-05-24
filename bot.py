import discord
from discord.ext import commands
import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='?')

dataDict = { 
             'categories' : [],
             'values' : [],
             'rankNames' : [],
             'rankImgs' : [],
             'rankColors' : []
           }

valContent = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_command_error(ctx, error):
    if (type(error) == discord.ext.commands.errors.CommandNotFound):
        print(error)
        await ctx.send(error)
    else:
        print(error)
        await ctx.send("There is an error with your command")

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
# Only call to make a request for valContent if the database / locally stored data is there are any changes in data
@bot.command()
async def valrank(ctx, *,username: str):
    # try:
        user = username.split("#")
        locale = "en-US"

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        playerInfo = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(user[0], user[1]), headers=headers)
        ranks = requests.get("https://valorant-api.com/v1/competitivetiers", headers=headers)
        valContent = requests.get("https://na.api.riotgames.com/val/content/v1/contents?locale={}&api_key={}".format(locale, os.getenv("VAL_API_KEY")))
        # leaderboards = requests.get("", headers=headers)
        # response4 = requests.get("https://dgxfkpkb4zk5c.cloudfront.net/leaderboards/affinity/{region}/queue/competitive/act/{actId}?startIndex={startIndex}&size={size}".format("NA", ""))



        print("Retrieving {}'s Ranked Stats...".format(user[0]))

        data = playerInfo.json()
        data2 = ranks.json()
        data3 = valContent.json()
        # data4 = response4.json()

        for x in data3:
            print(x)
        # print(data4)

        c = 0
        embed = discord.Embed()

        dataDict['categories'] = ["Rank", "Elo", "Last Match's Elo"]
        dataDict['values'] = [str(data['data']['currenttierpatched']), str(data['data']['ranking_in_tier']), str(data['data']['mmr_change_to_last_game'])]

        # Retrieves latest patch of ranked data and stores it locally (this way it runs faster without having to keep requesting from server)
        if (len(dataDict['rankNames']) <= 0):
            print("Retrieving New Valorant Data...")

            for i in data2['data'][-1]['tiers']:
                if ((type(i['tierName']) == str) and (type(i['largeIcon']) == str) and (type(i['color']) == str)):
                    dataDict['rankNames'].append(i['tierName'])
                    dataDict['rankImgs'].append(i['largeIcon'])
                    dataDict['rankColors'].append(i['color'])
                else:
                    continue
        else:
            print("Existing Valorant Data Found...")

        print("Embedding Valorant Data...")
        embed.title = "{}'s Ranked Stats".format(user[0])
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name=dataDict['categories'][0], value="{}".format(dataDict['values'][0]), inline=False)
        embed.add_field(name=dataDict['categories'][1], value="{} rr".format(dataDict['values'][1]), inline=False)
        embed.add_field(name=dataDict['categories'][2], value="{} rr".format(dataDict['values'][2]), inline=False)

        for i in range(len(dataDict['rankImgs'])):
            if (dataDict['values'][0].lower() == dataDict['rankNames'][i].lower()):
                embed.color = int("0x" + str(dataDict['rankColors'][i][:6]), 16)
                embed.set_thumbnail(url=dataDict['rankImgs'][i])

        await ctx.send(embed=embed)
        print("Successfully retrieved {}'s Stats!\n".format(user[0]))
    # except:
    #     await ctx.send("ERROR")

bot.run(os.getenv("DISCORD_TOKEN"))