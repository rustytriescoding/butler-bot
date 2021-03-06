import discord
from discord.ext import commands
import os
import requests
import datetime
import time
import re

valLeaderboard = []



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

#Searches database for id column and data argument, returns out column value
#I: MongoDB collection, data id, data argument 
#O: out value
def scanval(collection, id: str, data: str, out: str):
    query = collection.find_one({id : data})
    if query != None:
        return str(query[out])
    return None

#Checks if username argument is empty, ping, name
#I: server database, player username, message author id
#O: username array or error codes 0(empty), 1(ping doesnt have username stored), 2(invalid name)
def usernameCheck(database, name, id):

    userNamePattern = "^[^!\"\\#$%&'()*+,-./:;<=>?[\]@^_`{|}~]{3,16}#[a-zA-Z0-9]{1,5}"
    
    if name == None:  
        search = scanval(database, "_id", id, "valuser")
        if search != None:         
            user = search.split("#")
            return user
        else:
            return 0
    else:
        if "@" in name:         
            name = int(re.sub("[@<>]","", name))    
            search = scanval(database, "_id", name, "valuser")         
            if search != None:
                user = search.split("#")
                return user
            else:
                return 1
        else:
            if(re.search(userNamePattern, name)):
                user = name.split("#")
                return user
            else:
                return 2
   
#Retrieves JSON data from api urls
#I: url string key, player username, player tag, gamemode
#O: JSON data from api 
def retrieveData(url, username=None, tag=None, gamemode=None):
    urls = {
        "accountData" : "https://api.henrikdev.xyz/valorant/v1/account/{}/{}".format(username, tag),
        "mmrData" : "https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}".format(username, tag),
        "mmrHistory" : "https://api.henrikdev.xyz/valorant/v1/mmr-history/na/{}/{}".format(username, tag),
        "matchHistory" : "https://api.henrikdev.xyz/valorant/v3/matches/na/{}/{}{}".format(username, tag, "?filter="+str(gamemode)),
        "serverStatus" : "https://api.henrikdev.xyz/valorant/v1/status/na",
        "content" : "https://api.henrikdev.xyz/valorant/v1/content",
        "storeOffers" : "https://api.henrikdev.xyz/valorant/v1/store-offers",
        "storeFeatured" : "https://api.henrikdev.xyz/valorant/v1/store-featured",
        "ranks" : "https://valorant-api.com/v1/competitivetiers"
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    data = requests.get(urls[url], headers=headers)

    return data.json()
    
