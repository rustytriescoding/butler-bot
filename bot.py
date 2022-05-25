import discord
from discord.ext import commands
import os
import requests
import datetime
from dotenv import load_dotenv
import external_functions as EF

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix = "?", intents=intents)

dataDict = { 
             'categories' : [],
             'values' : [],
             'rankNames' : [],
             'rankImgs' : [],
             'rankColors' : []
           }

valContent = []
valLeaderboard = []

@bot.event
async def on_ready():
    # userID = 338492851040157696 -> for Baldar
    # channelID = 831017916354920468 -> for lounge chat
    userID = 235088799074484224
    channelID = 977787584178708480
    channel = bot.get_channel(channelID)

    print(bot.user.name + ' is now online')
    await channel.send('<@{}>'.format(userID) + ' Baldar Butler at your service!')

    await bot.change_presence(
        status = discord.Status.online,											                # Status: online, idle, dnd, invisible
        activity = discord.Game('Baldar Butler at your Service!'),
    )

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

@bot.command()
async def status(ctx):
    categories = ["Members", "Bots", "Online", "Offline"]
    values = [0, 0, 0, 0]
    imageURL = "https://cdn.discordapp.com/avatars/977770675584532520/1770496d2c1ec081b02a2f769d232c6e.webp?size=100"

    for guild in bot.guilds:
        for user in guild.members:
            if (user.bot == False):
                if (user.status != discord.Status.offline):
                    values[2] += 1
                else:
                    values[3] += 1
                values[0] += 1
            else:
                values[1] += 1

    embed = discord.Embed()
    embed.title = "{} Server Status".format(ctx.guild.name)
    embed.timestamp = datetime.datetime.utcnow()
    embed.color = 0xf04e1f
    embed.set_footer(text="\u200b", icon_url=imageURL)
    # embed.add_field(name="{}\t{}\t{}\t{}".format(categories[0], categories[1], categories[2], categories[3]), value="{}\    \    {}{}{}".format(memberCount, botCount, onlineMembers, offlineMembers), inline=True)
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(name=categories[0], value=values[0], inline=False)
    embed.add_field(name=categories[1], value=values[1], inline=False)
    embed.add_field(name=categories[2], value=values[2], inline=False)
    embed.add_field(name=categories[3], value=values[3], inline=False)
    embed.add_field(name="\u200b", value="\u200b")

    await ctx.channel.send(embed=embed)


# Make the bot faster at loading ranked info by:
# 1. Storing user data into a database / 
# Only call to make a request for valContent if the database / locally stored data is there are any changes in data
@bot.command()
async def valrank(ctx, *, username: str):
    try:
        user = username.split("#")

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        playerInfo = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(user[0], user[1]), headers=headers)
        ranks = requests.get("https://valorant-api.com/v1/competitivetiers", headers=headers)
        # valContent = requests.get("https://na.api.riotgames.com/val/content/v1/contents?locale={}&api_key={}".format(locale, os.getenv("VAL_API_KEY")))

        print("Retrieving {}'s Ranked Stats...".format(user[0]))

        data = playerInfo.json()
        data2 = ranks.json()
        
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

        # if (len(valLeaderboard) == 0):
        #     EF.requestLeaderboardData()
        
        rankNumber = EF.findLeaderboardRanking(user[0], user[1])
        lastElo = dataDict['values'][2]

        # Adds a number if they are on the leaderboard
        if (rankNumber >= 1):
            embed.add_field(name=dataDict['categories'][0], value="{} #{}".format(dataDict['values'][0], rankNumber), inline=False)
        elif ((dataDict['values'][0].lower().find('immortal') == 0) or (dataDict['values'][0].lower().find('radiant') == 0)):
            embed.add_field(name=dataDict['categories'][0], value="{} #?".format(dataDict['values'][0]), inline=False)
        else:
            embed.add_field(name=dataDict['categories'][0], value="{}".format(dataDict['values'][0]), inline=False)
        

        embed.add_field(name=dataDict['categories'][1], value="{} rr".format(dataDict['values'][1]), inline=False)
        if (type(lastElo) is not None):
            if (int(lastElo) >= 0):
                embed.add_field(name=dataDict['categories'][2], value="+{} rr".format(lastElo), inline=False)
            else:
                embed.add_field(name=dataDict['categories'][2], value="{} rr".format(lastElo), inline=False)
        else:
            embed.add_field(name=dataDict['categories'][2], value="{} rr".format(lastElo), inline=False)

        for i in range(len(dataDict['rankImgs'])):
            if (dataDict['values'][0].lower() == dataDict['rankNames'][i].lower()):
                embed.color = int("0x" + str(dataDict['rankColors'][i][:6]), 16)
                embed.set_thumbnail(url=dataDict['rankImgs'][i])

        await ctx.send(embed=embed)
        print("Successfully retrieved {}'s Stats!\n".format(user[0]))
    except:
        await ctx.send("Invalid Username")

# @bot.command()
# async def valtop(ctx):



bot.run(os.getenv("DISCORD_TOKEN"))