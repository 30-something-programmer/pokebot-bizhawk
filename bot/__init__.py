from os.path import dirname,abspath
class Bot():
    """
    Bot brings all of the other modules together to generate a fully functional bot
    """  

    # Import all methods
    import os,sys,logging,fastjsonschema,json,mmap, copy, math, time, pydirectinput, cv2
    import pandas as pd
    from threading import Thread
    from datetime import datetime
    from logging.handlers import RotatingFileHandler
    from discord_webhook import DiscordWebhook, DiscordEmbed
    from PIL import Image, ImageFile
    from ruamel.yaml import YAML
    from enum import Enum
    from flask_cors import CORS
    from ._config import config_schema, GetConfig
    from ._start import Start
    from ._stop import Stop
    from ._inputs import HoldButton,ReleaseAllInputs,ReleaseButton,PressButton,ButtonCombo,WaitFrames,default_input
    from ._catchBlockList import GetBlockList,BlockListManagement
    from ._customCatchConfig import CustomCatchConfig
    from ._customHooks import CustomHooks
    from ._discord import DiscordMessage, DiscordRichPresence
    from ._image import DetectTemplate
    from ._menuing import StartMenu,BagMenu,PickupItems,SaveGame,ResetGame,CatchPokemon,BattleOpponent,IsValidMove,FindEffectiveMove,FleeBattle
    from ._stats import GetEncounterLog,GetEncounterRate,GetRNGState,GetShinyLog,GetStats,EncounterPokemon,LogEncounter,OpponentChanged, session_encounters
    from ._files import WriteFile, ReadFile
    from ._catchBlockList import block_schema
    from ._navigation import Bonk, FollowPath, PlayerOnMap
    from .mmf.bag import GetBag, bag_schema
    from .mmf.common import LoadJsonMmap
    from .mmf.trainer import trainer_schema, GetTrainer
    from .mmf.emu import emu_schema, LangISO, clamp, GetEmu
    from .mmf.pokemon import pokemon_schema, natures, hiddenPowers, EnrichMonData, GetOpponent, GetParty
    from .mmf.screenshot import GetScreenshot
    from .mmf.trainer import trainer_schema, GetTrainer
    from .gen3.general import ModeBonk,ModeBunnyHop,ModeCoords,ModeFishing,ModePetalburgLoop,ModePremierBalls,ModeSpin,ModeSweetScent,AutoStop
    from .gen3.giftPokemon import CollectGiftMon,ModeBeldum,ModeCastform,ModeFossil,ModeJohtoStarters
    from .gen3.legendaries import ModeDeoxysPuzzle,ModeDeoxysResets,ModeGroudon,ModeHoOh,ModeKyogre,ModeLugia,ModeMew,ModeRayquaza,ModeRegis,ModeSouthernIsland
    from .gen3.starters import ModeStarters
    from .data.mapData import mapRSE
    from .data.gameState import GameState
    from .data.pokedexGenerator import GenerateDex

    # Set global variables
    ImageFile.LOAD_TRUNCATED_IMAGES = True    
    last_opponent_personality = None
    no_sleep_abilities = ["Shed Skin", "Insomnia", "Vital Spirit"]
    pickup_pokemon = ["Meowth", "Aipom", "Phanpy", "Teddiursa", "Zigzagoon", "Linoone"]

    

    # Initialization
    def __init__(self, profile, profilePath, logLevel):
        self.name = profile
        self.isRunning = True
        print('Bot "' + self.name + '" initialised')
        
        # Validate schema - comes from the mmf, sometimes it sends junk
        self.bagValidator = self.fastjsonschema.compile(self.bag_schema)  
        self.EmuValidator = self.fastjsonschema.compile(self.emu_schema)  
        self.pokemonValidator = self.fastjsonschema.compile(self.pokemon_schema)  
        self.TrainerValidator = self.fastjsonschema.compile(self.trainer_schema)

        # Set up the logger
        try:

            logPath = self.os.path.abspath(self.os.path.join(profilePath, 'logs'))
            logFormatter = self.logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(line:%(lineno)d) %(message)s')
            consoleFormatter = self.logging.Formatter('%(asctime)s - %(message)s')
            logName = self.datetime.utcnow().strftime('%Y-%m-%d')
            logFile = logPath + "/" + logName
            print("setting up log  file - " + logFile)
            self.os.makedirs(logPath, exist_ok=True)  # Create logs directory if not exist

            # Set up log file rotation handler
            logHandler = self.RotatingFileHandler(logFile, maxBytes=20 * 1024 * 1024, backupCount=5)
            logHandler.setFormatter(logFormatter)
            logHandler.setLevel(self.logging.INFO)

            # Set up console log stream handler
            consoleHandler = self.logging.StreamHandler()
            consoleHandler.setFormatter(consoleFormatter)
            consoleHandler.setLevel(logLevel)

            # Create logger and attach handlers
            self.logger = self.logging.getLogger(self.name)
            self.logger.setLevel(logLevel)
            self.logger.addHandler(logHandler)
            self.logger.addHandler(consoleHandler)
            self.logger.info("Logger set up successfully")
            self.logger.info("Logger mode:" + str(logLevel))
            self.logging.basicConfig(level=logLevel)

        except Exception as e:
            print(str(e))
            print("NOOOOOOOOOOOOOO! There was an error when setting up the logger - details above")
            input("Press enter to continue")
            self.os._exit(1)
        
        # Load the config
        configFile = self.os.path.join(profilePath, "config.yml")
        self.config = self.GetConfig(configFile)
                
        # Load folders for stats
        self.stats_folder = self.os.path.join(profilePath, "stats")
        self.os.makedirs(self.stats_folder, exist_ok=True)
        self.catchBlockListYmlFile = self.os.path.join(profilePath,"stats\CatchBlockList.yml")
        self.files = {
            "encounter_log": self.stats_folder + "/encounter_log.json",
            "shiny_log": self.stats_folder + "/shiny_log.json",
            "totals": self.stats_folder + "/totals.json"
        }
        self.session_encounters = 0

        # Validate Python
        try:
            MinMajorVersion = 3
            MinMinorVersion = 10
            MajorVersion = self.sys.version_info[0]
            MinorVersion = self.sys.version_info[1]

            if MajorVersion < MinMajorVersion or MinorVersion < MinMinorVersion:
                self.logger.error(
                    f"\n\nPython version is out of date! (Minimum required version for pokebot is "
                    f"{MinMajorVersion}.{MinMinorVersion})\nPlease install the latest version at "
                    f"https://www.python.org/downloads/\n")
                input("Press enter to continue...")
                self.os._exit(1)

            self.logger.info(f"Running pokebot on Python {MajorVersion}.{MinorVersion}")
            self.logger.info("Loading trainer details")
            while not self.GetTrainer():
                self.logger.error(
                    "\n\nFailed to get trainer data, unable to initialize pokebot!\nPlease confirm that `pokebot.lua` is "
                    "running in BizHawk, keep the Lua console open while the bot is active.\nIt can be opened through "
                    "'Tools > Lua Console'.\n")
                input("Press enter to try again...")

            self.logger.info(f"Mode: {self.config['bot_mode']}")

        except Exception as e:
            self.logger.exception(str(e))
            self.os._exit(1)

        # Validate the Game
        emu = self.GetEmu()
        if any([x in emu["detectedGame"] for x in ["Emerald"]]):  # "Ruby", "Sapphire"
            self.MapDataEnum = self.mapRSE
        # if any([x in emu["detectedGame"] for x in ["FireRed", "LeafGreen"]]):
        #    MapDataEnum = mapFRLG
        else:
            self.logger.error("Unsupported game detected...")
            input("Press enter to continue...")
            self.os._exit(1)

        # For the _catchBlockList method, set variables +and run the checker
        self.BlockListValidator = self.fastjsonschema.compile(self.block_schema)  # Validate the config file to ensure user didn't do a dumb

        # Create block list file if doesn't exist        
        if not self.os.path.exists(self.catchBlockListYmlFile):
            self.WriteFile(self.catchBlockListYmlFile, "block_list: []")
        
        # Load in json files
        self.data_folder = self.os.path.join(dirname(dirname(abspath(profilePath))),"bot","data")
        self.interface_folder = self.os.path.join(dirname(dirname(abspath(profilePath))),"bot","interface")      # Used for HTTP server _flaskserver.py
        self.item_list = self.json.loads(self.ReadFile(self.data_folder + "/items.json"))
        self.location_list = self.json.loads(self.ReadFile(self.data_folder + "/locations.json"))
        self.move_list = self.json.loads(self.ReadFile(self.data_folder + "/moves.json"))
        self.pokemon_list = self.json.loads(self.ReadFile(self.data_folder + "/pokemon.json"))
        self.PokedexList = self.json.loads(self.ReadFile(self.data_folder + "/pokedex.json"))
        self.type_list = self.json.loads(self.ReadFile(self.data_folder + "/types.json"))

        self.logger.info("data folder = "+self.data_folder)
        self.logger.info("interface folder = "+self.interface_folder)

        # For the inputs method, set variables
        self.input_list_mmap = self.mmap.mmap(-1, 4096, tagname="bizhawk_input_list-" + self.config["profile"],access=self.mmap.ACCESS_WRITE)
        self.input_list_mmap.seek(0)
        self.hold_input_mmap = self.mmap.mmap(-1, 4096, tagname="bizhawk_hold_input-" + self.config["profile"],access=self.mmap.ACCESS_WRITE)
        self.hold_input = self.default_input
        self.g_current_index = 1  # Variable that keeps track of what input in the list we are on.
        for i in range(100):  # Clear any prior inputs from last time script ran in case you haven't refreshed in Lua
            self.input_list_mmap.write(bytes('a', encoding="utf-8"))
