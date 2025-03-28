import json
import discord
import os
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_config(config):
    with open("config.json", "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)

config = load_config()
video_topics = list(config.get("videos", {}).keys())

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def video_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=topic, value=topic)
        for topic in video_topics if current.lower() in topic.lower()
    ][:25]


@tree.command(
    name="video",
    description="Send a video about a topic to a given User!",
)
@app_commands.describe(
    topic="The topic of the video",
    user="The user who will receive the video"
)
@app_commands.choices()
@app_commands.autocomplete(topic=video_autocomplete)
async def video_command(interaction: discord.Interaction, topic: str, user: discord.User):
    if topic.lower() not in config["videos"]:
        await interaction.response.send_message(f"Sorry, but **{topic}** is not a valid topic.")
        return

    video_url = config["videos"][topic.lower()]
    ignored_users = config.get("ignored_users", [])

    if user.id in ignored_users:
        await interaction.response.send_message(f"Hey {user.name}, here's a video about **{topic}**:\n{video_url}")
        await interaction.followup.send(f"You are not allowed to ping **{user.name}**!", ephemeral=True)
    else:
        await interaction.response.send_message(f"Hey {user.mention}, here's a video about **{topic}**:\n{video_url}")


@tree.command(
    name="ping-disable",
    description="Opt yourself out or back into being pinged.",
)
async def ping_disable(interaction: discord.Interaction):
    user_id = interaction.user.id
    ignored_users = config.get("ignored_users", [])

    if user_id in ignored_users:
        ignored_users.remove(user_id)
        action = "You will now be pinged in video messages."
    else:
        ignored_users.append(user_id)
        action = "You wont be pinged in video messages now."

    config["ignored_users"] = ignored_users
    save_config(config)

    await interaction.response.send_message(f"{action}", ephemeral=True)

@tree.command(
    name="info",
    description="General information about the bot",
)
async def info_command(interaction: discord.Interaction):
    message = (
        "**Bot Infos**\n"
        "Use `/video <topic> <user>` to send a video.\n"
        "Use `/ping-disable` to opt in or out of being pinged.\n\n"
        "Made with :heart: by <@873944359849066588> and <@78860870523826176>\n"
        "Source Code: <https://github.com/Wueffi/MattBotWings>"
    )
    await interaction.response.send_message(message, ephemeral=True)


@client.event
async def on_ready():
    await tree.sync()

    guild = discord.utils.get(client.guilds, id=841473212763734027) # Redstone Army

    if guild:
        status_text = "Redstone Army"
    else:
        status_text = "the ORE Network"

    activity = discord.Game(name=f"on {status_text}")
    await client.change_presence(activity=activity)

    print("Ready!")

if TOKEN:
    client.run(TOKEN)
else:
    print("ERROR: Bot token missing!")
