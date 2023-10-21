# This script will run a pokebot
import os
from bot import Bot

file_path = os.path.realpath(__file__)
profile = "example"
profile_folder = os.path.join(file_path,profile)

# Run the bot with a profile and a bot as the same name as the profie
bot = Bot(profile_folder,profile)
bot.Start()