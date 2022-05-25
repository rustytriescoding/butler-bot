import discord
from discord.ext import commands
import os
import requests
import datetime
from dotenv import load_dotenv
import time
import json

load_dotenv()

bot = commands.Bot(command_prefix='?')

dataDict = { 
             'categories' : [],
             'values' : [],
             'rankNames' : [],
             'rankImgs' : [],
             'rankColors' : []
           }

valContent = []
valLeaderboard = []

#Discord Bot Startup
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
async def valrank(ctx, *, username: str = None):

    if username == None:
        print("no username entered")
        await ctx.send("No username entered")

        #Call to mongodb
        #if username stored
        #username = mongodb value
        #else
        #no username entered or stored, add username with ?valusername
    else:
                


        user = username.split("#")

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        playerInfo = requests.get("https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(user[0], user[1]), headers=headers)
        ranks = requests.get("https://valorant-api.com/v1/competitivetiers", headers=headers)
        # valContent = requests.get("https://na.api.riotgames.com/val/content/v1/contents?locale={}&api_key={}".format(locale, os.getenv("VAL_API_KEY")))
        # leaderboards = requests.get("https://na.api.riotgames.com/val/ranked/v1/leaderboards/by-act/{}?size=200&startIndex=200&api_key={}".format(os.getenv("VAL_API_KEY")), headers=headers)

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

        #Comment out for no leaderboard
        # if (len(valLeaderboard) == 0):
            # requestLeaderboardData()
        
        
        rankNumber = findLeaderboardRanking(user[0], user[1])
        lastElo = dataDict['values'][2]

        print(int(lastElo) >= 0)

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

def requestLeaderboardData():
    locale = "en-US"
    headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://developer.riotgames.com"
              }

    print("Retrieving Current Act")

    valContent = requests.get("https://na.api.riotgames.com/val/content/v1/contents?locale={}&api_key={}".format(locale, os.getenv("VAL_API_KEY")), headers=headers)
    
    data3 = valContent.json()
    currentActID = ""
    c = 0
    reqs = 0

    for x in data3['acts']:
        if (x['name'].find('ACT') != 0):
            data3['acts'].pop(c)
        c += 1

    currentActID = data3['acts'][-1]['id']

    leaderboards = requests.get("https://na.api.riotgames.com/val/ranked/v1/leaderboards/by-act/{}?size={}&startIndex={}&api_key={}".format(currentActID, 1, 0, os.getenv("VAL_API_KEY")), headers=headers)
    
    print("Retrieved Leaderboard Data...")

    data4 = leaderboards.json()
    totalTopPlayers = data4['totalPlayers']
    
    for i in range(0, totalTopPlayers, 200):
        print("Retrieving players: {}-{}".format(i, i+200))
        leaderboards = requests.get("https://na.api.riotgames.com/val/ranked/v1/leaderboards/by-act/{}?size={}&startIndex={}&api_key={}".format(currentActID, 200, i, os.getenv("VAL_API_KEY")), headers=headers)
        
        playerData = leaderboards.json()
        # print(playerData['players'])
        if ('players' in playerData):
            valLeaderboard.append(playerData['players'])
        
        reqs += 1

        # Change the time.sleep rates after and have it running in the background putting data in a mongodb database
        if ((reqs % 10 == 0 and reqs != 0) or leaderboards.status_code == 429):
            print("Delaying Requests...")
            time.sleep(5)
        time.sleep(0.5)

def findLeaderboardRanking(username, tag):
    for dataGroup in valLeaderboard:
        for player in dataGroup:
            if (('gameName' in player) and ('tagLine' in player)):
                if (player['gameName'].lower() == username.lower()) and (player['tagLine'].lower() == tag.lower()):
                    rankNumber = player['leaderboardRank']
                    print("{}#{} has been found! They are top #{}".format(player['gameName'], player['tagLine'], rankNumber))
                    return rankNumber
    return -1

bot.run(os.getenv("DISCORD_TOKEN"))