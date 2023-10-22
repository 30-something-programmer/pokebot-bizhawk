# This script will run a pokebot
import logging, os
from os.path import dirname, abspath
from bot import Bot


""" LOGGING
    See https://realpython.com/python-logging/
    Order is DEBUG > INFO > WARNING > ERROR > CRITICAL
"""
logLevel = logging.WARNING 

""" PROFILES
    Each bot runs as a profile. Meaning it has its own script, instance, logging and stats
    Setting the name here MUST match a folder too    
    
"""

profile = "example"

    #TODO   - If a profile does not exist, auto-generate one from example
    #TODO   - Use the profile names as an 

parentPath = dirname(abspath(__file__))
profilePath = os.path.join(parentPath, "profiles", profile)

# Run the bot with a profile and a bot as the same name as the profie
bot = Bot(profile, profilePath, logLevel)
bot.Start()