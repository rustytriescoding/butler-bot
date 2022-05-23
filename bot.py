import discord
from discord.ext import commands
import os
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
    # userID = 338492851040157696
    # channelID = 831017916354920468
    userID = 235088799074484224
    channelID = 977787584178708480
    channel = bot.get_channel(channelID)
    print(bot.user.name + ' is now online')
    for i in range (5):
        await channel.send('<@{}>'.format(userID) + ' Baldar Butler at your service!')
    await bot.change_presence(
        status = discord.Status.online,											                # Status: online, idle, dnd, invisible
        activity = discord.Game('Baldar Butler at your Service!'),
    )

@bot.command()
async def status(ctx):
    categories = ["Total Members:", "Total Bots:", "Online:", "Offline:"]
    memberCount = 0
    botCount = 0
    onlineMembers = 0
    offlineMembers = 0

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

    embed = discord.Embed(title="New Age Server Status", color = 0xf04e1f)

    # await ctx.channel.send("{} {}".format(categories[0], memberCount))
    # await ctx.channel.send("{} {}".format(categories[1], botCount))
    # await ctx.channel.send("{} {}".format(categories[2], onlineMembers))
    # await ctx.channel.send("{} {}".format(categories[3], offlineMembers))
    await ctx.channel.send(embed)

bot.run(os.getenv("DISCORD_TOKEN"))