import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import datetime
from openai import OpenAI
from jokeapi import Jokes
import requests
from heros import dota_heroes  # Importing dota_heroes from a custom module
from keep_alive import keep_alive
"""Basic Bot config"""

#keep server up#
keep_alive()
# Load .env file
load_dotenv()

# Retrieve the Discord API key from the environment
DISCORD_KEY = os.getenv("DISCORD_KEY")

# Define intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Allow the bot to read message content
bot = commands.Bot(
    command_prefix="$", intents=intents
)  # Define the bot with prefix '$'


# Event handler for when the bot is ready
@bot.event
async def on_ready():
    try:
        sync = await bot.tree.sync()

        # Print status message when the bot is ready
        print("Starting {} BOT at {}".format(bot.user, datetime.datetime.now()))
        print("Bot command tree synced")
        send_live_message.start()
        
    except Exception as e:
        # Print error if there's an issue loading the bot
        print("Error Loading bot", e)
        return


"""AI commands"""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
gpt_model = "gpt-3.5-turbo"


# Event handler for when a message is sent in the chat
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Handle special command '$jared' to interact with OpenAI
    if "$jared" in message.content:
        try:
            prompt = message.content[5:]  # Extract the message content after '$jared'
            print(prompt)  # Print the received message for debugging

            # Send the message to OpenAI for completion
            res = client.chat.completions.create(
                model=gpt_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. You are serving as a Discord bot, so keep your responses Discord chat-like.",
                    },
                    {
                        "role": "user",
                        "content": prompt,  # User's input
                    },
                ],
            )

            # Send the completed response back to the channel
            await message.channel.send(res.choices[0].message.content)

        except Exception as e:
            # Print error if there's an issue fetching data from OpenAI
            print("Error fetching data!", e)
            await message.channel.send("Error fetching data")
            return


# Command for getting a fun fact about a topic
@bot.hybrid_command(name="funfact", description="Fun fact about a topic")
async def funfact(ctx, topic):
    # Get a fun fact from OpenAI based on the provided topic
    response = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": "You provide anime suggestions based on a category.",
            },
            {
                "role": "user",
                "content": f"Please give me a fun fact about {topic}. Please respond like this: 'Fun Fact: *your fact here*'.",
            },
        ],
    )

    # Send the fun fact response back to the channel
    await ctx.send(response.choices[0].message.content)


# Command for requesting an anime suggestion
@bot.hybrid_command(name="anime", description="Request anime suggestion")
async def anime(ctx, category):
    try:
        # Get an anime suggestion from OpenAI based on the provided category
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {
                    "role": "system",
                    "content": "You provide anime suggestions based on a category.",
                },
                {
                    "role": "user",
                    "content": f"Give me 1 anime suggestion under the category {category}. Respond like this: 'Anime: *insert title*\n\nDescription:*include a quick spoiler-free description*\n\nSeasons: *number of seasons* Total Episode: *total number of episodes* Average Episode Time: *average episode time*",
                },
            ],
        )

        # Send the anime suggestion response back to the channel
        await ctx.send(response.choices[0].message.content)

    except Exception as e:
        # Print error if there's an issue fetching data from OpenAI
        print("Error fetching OPENAI_API", e)
        await ctx.send("Error fetching OPENAI_API")
        return


"""For fun commands"""


# Command for fetching a dark joke
@bot.hybrid_command(name="joke", description="WARNING DARK JOKES!")
async def fetch_joke(ctx):
    try:
        # Initialize the Jokes class and fetch a dark joke
        j = await Jokes()
        joke = await j.get_joke(category=["dark"])

        # Check the type of joke and send it accordingly
        if joke["type"] == "single":
            await ctx.send(joke["joke"])
        else:
            joke_text = "{}\n{}".format(joke["setup"], joke["delivery"])
            await ctx.send(joke_text)

    except:
        # Print error if there's an issue fetching data from the Joke API
        print("Error fetching JOKE API")
        return


"""Dota 2 commands"""
# List of Dota 2 players
players = (
    {"name": "ricardo", "id": 152428288},
    {"name": "skrptz", "id": 1029733554},
    {"name": "bub", "id": 106210714},
    {"name": "jeo", "id": 232061338},
    {"name": "yeh-c", "id": 106108405},
    {"name": "roaming", "id": 86331243},
    {"name": "shocked", "id": 111004470},
    {"name": "manifest", "id": 106087035},
    {"name": "tynche", "id": 137734728},
    {"name": "rando", "id": 309302993},
)

# Game modes in Dota 2
game_modes = [
    {"id": 0, "name": "None"},
    {"id": 1, "name": "All Pick"},
    {"id": 2, "name": "Captain's Mode"},
    {"id": 3, "name": "Random Draft"},
    {"id": 4, "name": "Single Draft"},
    {"id": 5, "name": "All Random"},
    {"id": 6, "name": "Intro"},
    {"id": 7, "name": "Diretide"},
    {"id": 8, "name": "Reverse Captain's Mode"},
    {"id": 9, "name": "The Greeviling"},
    {"id": 10, "name": "Tutorial"},
    {"id": 11, "name": "Mid Only"},
    {"id": 12, "name": "Least Played"},
    {"id": 13, "name": "Limited Heroes"},
    {"id": 14, "name": "Compendium Matchmaking"},
    {"id": 15, "name": "Ability Draft"},
    {"id": 16, "name": "All Random Deathmatch"},
    {"id": 17, "name": "1v1 Mid"},
    {"id": 18, "name": "All Draft"},
    {"id": 19, "name": "Turbo"},
    {"id": 20, "name": "Mutation"},
    {"id": 21, "name": "Cavern"},
    {"id": 22, "name": "Ranked Roles"},
    {"id": 23, "name": "Turbo"},
]


# /players
@bot.hybrid_command(name="players", description="Get a list of registered Dota players")
async def call_players(ctx):
    player_array = []

    for i in players:
        player_array.append(i.get("name"))

    await ctx.send("\n".join(player_array))


# Helper function to search for a player
def searchPlayer(name, players):
    for player in players:
        if player.get("name") == name:
            return player

    print("Could not find player '{}'".format(name))
    return


# Helper function to get the game mode name based on ID
def get_game_mode(match):
    for mode in game_modes:
        if mode.get("id") == match["game_mode"]:
            return mode["name"]

    return "Unknown"


# Command for fetching recent matches of a player
@bot.hybrid_command(
    name="recent", description="Look up last 1-5 recent matches for Dota player"
)
async def recent(ctx, limit, player_name):
    if int(limit) > 5:
        # Limit the number of matches to 5 for performance reasons
        print("User {} tried to fetch more than 5 matches".format(ctx.author))
        await ctx.send("For more than 5 matches please visit opendota.com")
        return

    player = searchPlayer(player_name, players)
    final_message = []  # List to store final message lines
    ##check if player requested in registered
    if player is not None:
        DOTA_KEY = os.getenv("DOTA_KEY")
        url = f"https://api.opendota.com/api/players/{player['id']}/Matches?limit={limit}&significant=0&api_key={DOTA_KEY}"

    else:
        await ctx.send("!Player not registered! Ask admin to register...")
        return

    # Fetch data from OpenDota API
    res = requests.get(url=url)
    data = res.json()

    # Loop through each match data and format message lines
    for match in data:
        for hero in dota_heroes:
            if hero.get("id") == match["hero_id"]:
                played_hero = hero["name"]  # Get the hero name

        if (match["radiant_win"] == 1 and match["player_slot"] < 128) or (
            match["radiant_win"] == 0 and match["player_slot"] >= 128
        ):
            match_results = "Match won"
        else:
            match_results = "Match Lost"
        # Format the message lines for each match
        message_lines = (
            f"--{match_results}--\n"
            f"Player: {player['name']}\n"
            f"ID #{match['match_id']} Mode: {get_game_mode(match=match)}\n"
            f"Duration: {str(round(int(match['duration'] / 60), 2))} mins\n"
            f"Hero: {played_hero}\n"
            f"Kills: {match['kills']}\n"
            f"Deaths: {match['deaths']}\n"
            f"Assists: {match['assists']}"
        )

        final_message.append(message_lines)  # Add formatted message to the final list

    # Send the final message with all recent matches
    await ctx.send("\n\n".join(final_message))


# Command for fetching the last match of a player
@bot.hybrid_command(name="lastmatch", description="Look up Dota player's last match")
async def lastmatch(ctx, player_name):
    player = searchPlayer(player_name, players)
    if player is not None:
        DOTA_KEY = os.getenv("DOTA_KEY")
        url = f"https://api.opendota.com/api/players/{player['id']}/recentMatches?significant=0&api_key={DOTA_KEY}"
    else:
        await ctx.send("!Player not registered! Ask admin to register...")
        return

    try:
        res = requests.get(url=url)
        data = res.json()

        # Check if the data list is empty
        if not data:
            await ctx.send("No match data found for this player.")
            return

        match_data = data[0]  # Get the first match from the list

        # Check if the player won or lost
        if (match_data["radiant_win"] == 1 and match_data["player_slot"] < 128) or (
            match_data["radiant_win"] == 0 and match_data["player_slot"] >= 128
        ):
            match_results = "Match won"
        else:
            match_results = "Match Lost"

        # Find the hero's name from the hero ID
        played_hero = "Unknown"
        for hero in dota_heroes:
            if hero.get("id") == match_data["hero_id"]:
                played_hero = hero["name"]

        # Format the message with match details
        message_lines = (
            f"--{match_results}--\n"
            f"Player: {player['name']}\n"
            f"ID #{match_data['match_id']} Mode: {get_game_mode(match=match_data)}\n"
            f"Duration: {str(round(int(match_data['duration'] / 60), 2))} mins\n"
            f"Hero: {played_hero}\n"
            f"Kills: {match_data['kills']}\n"
            f"Deaths: {match_data['deaths']}\n"
            f"Assists: {match_data['assists']}"
        )

        # Send the formatted message to the channel
        await ctx.send(message_lines)

    except Exception as e:
        print("Error while fetching match data:", e)
        await ctx.send("An error occurred while fetching match data.")


##BOT STATUS##

@tasks.loop(minutes=3)  # Run the task every 30 minutes
async def send_live_message():
    channel = bot.get_channel(1226903209109491802)
    if channel:
        message = f"{datetime.datetime.now()} - Status - ACTIVE"
        await channel.send(message)


# Run the bot with the provided Discord API key
bot.run(DISCORD_KEY)


"""

--DISCORD BOT(JARED)--


This Discord bot application integrates various functionalities for entertainment and Dota 2 game statistics.
It features an AI chat functionality using OpenAI's GPT-3.5 model, allowing users to interact with the bot by
sending messages prefixed with '$jared' to receive AI-generated responses. The bot can also provide fun facts
on requested topics, suggest anime based on categories, and fetch dark jokes. In addition, it includes Dota 2
commands for fetching recent matches and the last match of registered players. The bot utilizes the OpenDota
API to retrieve match data and provides details such as match results, duration, hero played, kills, deaths,
and assists. The application is designed to engage users with a variety of entertaining and informative
features, enhancing the Discord server's functionality.

"""
