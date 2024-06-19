import discord
from discord.ext import commands
from discord import app_commands
import aiohttp  # Async HTTP requests
from dotenv import load_dotenv
from pathlib import Path
import os

# Define the path to the .env file in the parent directory
env_path = Path('..') / '.env'

# Load environment variables from the .env file
load_dotenv(dotenv_path=env_path)

# Get the token from the environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the intent to receive message content

# Initialize the bot with the specified intents
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Create an instance of app_commands.CommandTree for handling slash commands
tree = bot.tree

FLASK_API_URL = 'https://codeanster.pythonanywhere.com/status'

# Define trip_status globally
trip_status = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    for guild in bot.guilds:
        print(f'Available guild: {guild.name} (ID: {guild.id})')

    guild = bot.get_guild(467594016805093407)
    if guild is None:
        print("Guild not found or bot does not have access to the guild.")
        return

    tree.clear_commands(guild=guild)
    try:
        synced = await tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands:")
        for cmd in synced:
            print(f"  - {cmd.name}")
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@tree.command(name='status', description='Get the current trip status')
async def status(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        async with session.get(FLASK_API_URL) as response:
            if response.status == 200:
                trip_status = await response.json()
                print(trip_status)
                status_message = (f"Current Status: {trip_status['status']}\n"
                                  f"Location: {trip_status['location']}\n"
                                  f"Estimated Return: {trip_status['return_date']}\n"
                                  f"Map Link: https://share.garmin.com/2NGVX")
                photo_url = trip_status.get('photo_url', '')
                if photo_url:
                    # Construct the full path to the uploaded photo
                    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                    photo_path = f'{base_dir}/web/{photo_url}'
                    print(photo_path)
                    #photo_path = os.path.join(base_dir, 'web', photo_url)
                    #print(photo_path)
                    await interaction.response.send_message(status_message, file=discord.File(photo_path))
                else:
                    await interaction.response.send_message(status_message)
            else:
                await interaction.response.send_message("Failed to retrieve status.")

bot.run(DISCORD_TOKEN)