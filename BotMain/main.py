import asyncio
import discord
from discord.ext import commands,tasks
import random
import os
import time
import json
from itertools import cycle

#assign the address of your json file where you keep the default values of variables if you need them
globalVariable = None
#We get the reference for our bot in the form of client variable and assign its prefix, determine its intents. You can turn off case_insensitive command trigger and whitespace after prefix if you would like to conserve performance
client = commands.Bot(command_prefix="!",intents=discord.Intents.all(),case_insensitive=True,strip_after_prefix=True)
@client.event
async def on_ready():
    print("bot is Online")
    
# Bring value gets a single value from a Json file. Address is the address of the json file and the Uvariable is the identifier of the variable in the json file
def BringValue(address, Uvariable):
    f = open(address, "r")
    variable = json.load(f)
    print(f"Loaded the {address}, {Uvariable}:{variable[Uvariable]}")
    f.close()
    return variable[Uvariable]

# Write value overwrites or adds a new value on a json file. Address is the address of the file, Uvariable is the identifier and Value is the value we are saving
def WriteValue(address, Uvariable, Value):
    a_file = open(address, "r")
    json_object = json.load(a_file)
    a_file.close()
    print(f"Loaded the {address}")
    json_object[Uvariable] = Value
    a_file = open(address, "w")
    print(f"Wrote {Uvariable} : {Value} at {address}")
    json.dump(json_object, a_file, indent=5)
    a_file.close()

# Write value overwrites or adds a new value on a json file. Address is the address of the file, Uvariable is the identifier and Value is the value we are saving
def AddValue(address, Uvariable, Value):
    file = open(address, "r")
    variable = json.load(file)
    variable[Uvariable] = Value
    file.close()
    file = open(address, "w")
    json.dump(variable, file, indent=5)
    file.close()
    print(f"Adding new entry {Uvariable} : {Value} to {address} ")

#Load Cache returns the whole json file as a collection for read only purpose
def LoadCache(address):
    file = open(address, "r")
    variable = json.load(file)
    file.close()
    print(f"Loaded {variable} to ram from {address}")
    return variable

#Enter Cache overwrites a json file with the provided collection, be careful with it if you dont want to lose previously written data
def EnterCache(address, collection):
    file = open(address, "w")
    json.dump(collection, file, indent=5)
    file.close()
    print(f"Loaded the collection in ram to the disk.")

#EraseDefaults is useful if you want to trim out repeating information you dont want to keep to preserve space and keep your leaderboards tidy. Uvariable is the identifier of the default value saved in the global json file where you need to keep your  default values saved
def EraseDefaults(address, Uvariable):
    currentCache = LoadCache(address)
    default = BringValue(address=globalVariable, Uvariable=Uvariable)
    newCache = {}
    totalRemoved = 0
    for x in currentCache:
        if currentCache[x] != default:
            newCache[x] = currentCache[x]
        else:
            totalRemoved += 1
    EnterCache(address=address, collection=newCache)
    print(f"{totalRemoved} entries removed from {address}")

#this bot command will shutdown your bot
@client.command(hidden=True)
async def shutdown(ctx):
    await ctx.send("Bot is shutting down.")
    await client.close()


def externalUnload(extension):
    client.unload_extension(extension)
    print(f"unloaded {extension} ")

#this is useful for error messages, especially cooldowns which return seconds. This will format it into a more readable form and round it
def timeformatter(entry: float):
    text = "Hours"
    time = int(round(entry, 1) / 3600)  # hour
    if time == 0:
        time = int(round(entry, 1) / 60)  # minutes
        text = "Minutes"
    if time == 0:
        time = entry  # second
        text = "Seconds"
    text = f"{time} {text}"

    return text


@client.command(hidden=True)
async def ping(ctx):
    await ctx.send(f"Bot Latency = {round(client.latency, 2)}ms")
    print(f"Bot Latency = {round(client.latency, 2)}ms")


@client.command(hidden=True)
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    print(f"loaded {extension} ")
    await ctx.send(f"loaded {extension}")


@client.command(hidden=True)
async def reload(ctx, extension):
    await unload(ctx, extension)
    await load(ctx, extension)


@client.command(hidden=True)
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    print(f"unloaded {extension} ")
    await ctx.send(f"unloaded {extension}")


def leaderboard(address, number=10, order=True):
    all = LoadCache(address=address)
    a = sorted(all, key=all.get, reverse=order)
    length = len(a)
    if length > number:
        length = number
    number = 1
    t = """"""
    for x in range(length):
        t = t + f"""{number:,}. <@{a[number - 1]}> - {all[a[number - 1]]:,}

"""
        number = number + 1
    if t is None:
        t = "No data"

    return t


def inspectVariable(author, uvariable, address):
    try:
        value = BringValue(address=address, Uvariable=f"{author}")
    except:
        value = BringValue(address=globalVariable, Uvariable=uvariable)
        AddValue(address=address, Uvariable=f"{author}", Value=value)


def getrank(address, author):
    rank = 0
    cache = LoadCache(address)
    rankSuffix = ["th", "st", "nd", "rd"]
    s = sorted(cache, key=cache.get, reverse=True)

    for x in range(len(s)):

        if author == s[x]:
            rank += 1
            break
        rank += 1

    if rank % 10 in [1, 2, 3] and rank not in [11, 12, 13]:
        t = f"{rank}{rankSuffix[rank % 10]}"
    else:
        t = f"{rank}{rankSuffix[0]}"
    return t


for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")
        print(f"Loaded {filename[:-3]}")
try:
    token = BringValue("Token.json", "Token")
except:
    token = ""

if token == "":
    print("Token in the Token.json file is missing, please enter the bot token by hand:")
    token = input()
    WriteValue("Token.json", "Token", token)

# globalcache = LoadCache(address=globalVariable)

client.run(token)