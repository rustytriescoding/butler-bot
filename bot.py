from datetime import datetime
import discord
from discord.ext import commands
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix = "?", intents=intents)

@bot.event
async def on_ready():
    print('Logged in as', bot)

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

@bot.command()
async def status(ctx):
    categories = ["Members", "Bots", "Online", "Offline"]
    memberCount = 0
    botCount = 0
    onlineMembers = 0
    offlineMembers = 0
    imageURL = "https://cdn.discordapp.com/avatars/977770675584532520/1770496d2c1ec081b02a2f769d232c6e.webp?size=100"

    for guild in bot.guilds:
        for user in guild.members:
            if (user.bot == False):
                if (user.status != discord.Status.offline):
                    onlineMembers += 1
                else:
                    offlineMembers += 1
                memberCount += 1
            else:
                botCount += 1

    embed = discord.Embed()
    embed.title = "{} Server Status".format(ctx.guild.name)
    embed.timestamp = datetime.datetime.utcnow()
    embed.color = 0xf04e1f
    embed.set_footer(text="\u200b", icon_url=imageURL)
    # embed.add_field(name="{}\t{}\t{}\t{}".format(categories[0], categories[1], categories[2], categories[3]), value="{}\    \    {}{}{}".format(memberCount, botCount, onlineMembers, offlineMembers), inline=True)
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(name=categories[0], value=memberCount, inline=False)
    embed.add_field(name=categories[1], value=botCount, inline=False)
    embed.add_field(name=categories[2], value=onlineMembers, inline=False)
    embed.add_field(name=categories[3], value=offlineMembers, inline=False)
    embed.add_field(name="\u200b", value="\u200b")



    # await ctx.channel.send("{} {}".format(categories[0], memberCount))
    # await ctx.channel.send("{} {}".format(categories[1], botCount))
    # await ctx.channel.send("{} {}".format(categories[2], onlineMembers))
    # await ctx.channel.send("{} {}".format(categorgiies[3], offlineMembers))
    await ctx.channel.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))