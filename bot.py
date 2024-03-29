from types import NoneType
import discord
from discord.ext import commands
import os
import requests
import datetime
from dotenv import load_dotenv
import time
import json
import pymongo
from pymongo import MongoClient
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
userNamePattern = "^[^!\"\\#$%&'()*+,-./:;<=>?[\]@^_`{|}~]{3,16}#[a-zA-Z0-9]{1,5}"
emojiFinderPattern = "[^\w\s^!\"\\#$%&'()*+,-./:;<=>?[\]@^_`{|}~]"

cluster = MongoClient(os.getenv("MONGO_URL")) #add connection url to .env
server = cluster["servers"]
valusernames = server["val-data"]

#Discord Bot Startup
@bot.event
async def on_ready():
    channelID = 996534966622093333
    channel = bot.get_channel(channelID)

    print(bot.user.name + ' is now online')
    await channel.send('Baldar Butler at your service!')

    await bot.change_presence(
        status = discord.Status.online,	
        activity = discord.Game('Baldar Butler at your Service!'),
    )

#Error checking
@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("There are 1 or more missing arguments!")
    else:
        await ctx.send("There is an error with your command")



#Prints the skull emoji for the specified amount of times
#I: Number of skull emojis to print
#O: Prints skull emojis
@bot.command()
async def skull(ctx, userinput: str = None):
    try:
        if userinput == None:
            await ctx.send("Please enter a number between 1-2000")
            return
        
        num = int(userinput)
        if num < 1 or num > 2000:
            await ctx.send("Number out of range, number must be within 1-2000")
        else:
            await ctx.send('💀' * num)
    except ValueError:
        await ctx.send("Not a number!")

@bot.command()
async def status(ctx):
    categories = ["Online", "Offline", "Members", "Bots"]
    values = [0, 0, 0, 0]
    # imageURL = "https://cdn.discordapp.com/avatars/977770675584532520/1770496d2c1ec081b02a2f769d232c6e.webp?size=100"
    imageURL = ctx.author.avatar_url

    for guild in bot.guilds:
        for user in guild.members:
            if (user.bot == False):
                if (user.status != discord.Status.offline):
                    values[0] += 1
                else:
                    values[1] += 1
                values[2] += 1
            else:
                values[3] += 1

    embed = discord.Embed()
    embed.title = "{} Server Status".format(ctx.guild.name)
    embed.timestamp = datetime.datetime.utcnow()
    embed.color = 0xf04e1f
    embed.set_footer(text="\u200b", icon_url=imageURL)
    # embed.add_field(name="{}\t{}\t{}\t{}".format(categories[0], categories[1], categories[2], categories[3]), value="{}\    \    {}{}{}".format(memberCount, botCount, onlineMembers, offlineMembers), inline=True)
    embed.add_field(name=categories[0], value=values[0], inline=False)
    embed.add_field(name=categories[1], value=values[1], inline=False)
    embed.add_field(name=categories[2], value=values[2], inline=False)
    embed.add_field(name=categories[3], value=values[3], inline=False)

    await ctx.channel.send(embed=embed)

@bot.group()
async def val(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid val command passed')

#Cases
# 1. No username
# 2. Not string
# 3. Username invalid format
# 4. Username belongs to someone else in server (allow them to take it)
# 5. user already has username stored

# Test Cases
# 1.         < 3 chars
# 2.           3 chars
# 3.  > 3 & < 16 chars
# 4.          16 chars
# 5.        > 16 chars
# 6. Punctuation
# 7. Emojis
# 8. Pings / server channels
# 9. No hashtag
# 10. No argument provided
# 11. Alphanumeric only (1-5 chars) for tagline
# 12. Alphanumeric including weird symbols like (ツ, ｔｈｉｓ ｔｅｘｔ, etc)
# 13. Spaces between names
@val.command()
async def username(ctx, *, arg: str = None):
    # search = valdata.find_one({"valuser" : arg}) #Searches if username exists in database
    # if search != None:
    #     search = str(search["valuser"]) #Converts val username to string

    # Arg only picks up on the (v1 for v1 zander#swag)
    search = EF.scanval(valusernames, "valuser", arg, "valuser")
    
    if arg == None:
        await ctx.send("No username entered") 
    else:
        try:
            if ((len(re.findall(userNamePattern, arg)) == 1) and (len(re.findall(emojiFinderPattern, arg)) == 0)):
                print("This username is valid!")

                if arg == search:
                    query = {"_id": ctx.author.id}
                    newusername = { "$set": { "valuser": arg } }           
                    valusernames.update_one(query, newusername)
                    await ctx.send("Someone on this server already has this username, saving anyways")
                else:
                    myquery = { "_id": ctx.author.id }
                    if (valusernames.count_documents(myquery) == 0): #User does not exist in database, saving new name

                        post = {"_id": ctx.author.id, "valuser": arg}
                        valusernames.insert_one(post)

                        await ctx.send(arg + ": username is saved")
                    else: #User exists in database, updating name
                        query = {"_id": ctx.author.id}
                        newusername = { "$set": { "valuser": arg } }
                        
                        valusernames.update_one(query, newusername)
                        await ctx.send(arg + ": username is updated")
            else:
                print("This username is invalid!")
                await ctx.send("Please enter a valid username")
        except: 
            await ctx.send("Please enter a valid username")


# Make the bot faster at loading ranked info by:
# 1. Storing user data into a database / 
# Only call to make a request for valContent if the database / locally stored data is there are any changes in data
@val.command()
async def rank(ctx, *, username=None):
    
    user = EF.usernameCheck(valusernames, username, ctx.author.id)

    if user == 0:
        await ctx.send("You have no username stored. Add one by using ?val username")
        return
    elif user == 1:
        await ctx.send("No username stored on this account. Add one by using ?val username")
        return
    elif user == 2:
        await ctx.send("Invalid username entered")
        return
    

    # print("Retrieving {}'s Ranked Stats...".format(user[0]))

    data = EF.retrieveData("mmrData", user[0], user[1])
    data2 = EF.retrieveData("ranks")
    
    embed = discord.Embed()

    dataDict['categories'] = ["Rank", "Elo", "Last Match's Elo"]
    dataDict['values'] = [str(data['data']['currenttierpatched']), str(data['data']['ranking_in_tier']), str(data['data']['mmr_change_to_last_game'])]

    # Retrieves latest patch of ranked data and stores it locally (this way it runs faster without having to keep requesting from server)
    if (len(dataDict['rankNames']) <= 0):
        # print("Retrieving New Valorant Data...")

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

    # Comment out for no leaderboard number for immortal+ players
    # if (len(valLeaderboard) == 0):
        # EF.requestLeaderboardData()
    
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


@val.command()
async def comp(ctx, *, username=None):
    plt.style.use("dark_background")

    for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
        plt.rcParams[param] = '0.9'  # very light grey

    for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
        plt.rcParams[param] = '#212946'  # bluish dark grey

    user = EF.usernameCheck(valusernames, username, ctx.author.id)

    if user == 0:
        await ctx.send("You have no username stored. Add one by using ?val username")
        return
    elif user == 1:
        await ctx.send("No username stored on this account. Add one by using ?val username")
        return
    elif user == 2:
        await ctx.send("Invalid username entered")
        return

    playerData = EF.retrieveData("mmrHistory", user[0], user[1])

    elo = []
    match = []
    netElo = 0



    # for match in playerData['data']:
    #     netElo += int(match['mmr_change_to_last_game'])
    #     print("Elo per match" + str(match['mmr_change_to_last_game']))
    #     elo.insert(len(elo), netElo)       
    #     print(netElo)

    # match.extend(range(1, len(elo)))
    # print(match)


    for match in range(len(playerData['data']), 0, -1):
        netElo += int(playerData['data'][match -1]['mmr_change_to_last_game'])
        elo.append(netElo)









    # elo = [10, -20, 19, 15, -20, 16, 17, -21]

    colors = [
        '#08F7FE',  # teal/cyan
        '#FE53BB',  # pink
        '#F5D300',  # yellow
        '#00ff41',  # matrix green
    ]

    df = pd.DataFrame({'Net Elo': elo})
    # colors = np.where(df[elo] < 0, '#00ff41', '#FE53BB')
    


    
                    
    fig, ax = plt.subplots()

    df.plot(marker='o', color=colors, ax=ax)

    # Redraw the data with low alpha and slighty increased linewidth:
    n_shades = 10
    diff_linewidth = 1.05
    alpha_value = 0.3 / n_shades

    for n in range(1, n_shades+1):

        df.plot(marker='o',
                linewidth=2+(diff_linewidth*n),
                alpha=alpha_value,
                legend=False,
                ax=ax,
                color=colors)

    # Color the areas below the lines:
    # for column, color in zip(df, colors):
    #     ax.fill_between(x=df.index,
    #                     y1=df[column].values,
    #                     y2=[0] * len(df),
    #                     color=color,
    #                     alpha=0.1)

    plt.xlabel("Match")
    plt.ylabel("Elo")

    ax.grid(color='#2A3459')

    ax.set_xlim([ax.get_xlim()[0] - 0.2, ax.get_xlim()[1] + 0.2])  # to not have the markers cut off
    
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)


    # ax.get_xaxis().set_ticks([])
    # ax.get_yaxis().set_ticks([])
    # ax.set_ylim(0)
    plt.savefig("test.png") #, transparent=True
    plt.close()
    image = discord.File("test.png")
    await ctx.send(file=image)    


bot.run(os.getenv("DISCORD_TOKEN"))