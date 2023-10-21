
# Global imports
import os,sys,logging,fastjsonschema,json,mmap

# Specific Global imports
from logging.handlers import RotatingFileHandler
from discord_webhook import DiscordWebhook, DiscordEmbed

logLevel = logging.DEBUG # Use LogLevel DEBUG when debugging

class Bot():
    """
    Bot brings all of the other modules together to generate a fully functional bot
    """  

    # Import all methods
    from PIL import Image, ImageFile
    from ruamel.yaml import YAML
    from enum import Enum
    from _config import config_schema, GetConfig
    from _start import Start
    from _stop import Stop
    from _inputs import HoldButton,ReleaseAllInputs,ReleaseButton,PressButton,ButtonCombo,WaitFrames,default_input
    from _catchBlockList import GetBlockList,BlockListManagement
    from _customCatchConfig import CustomCatchConfig
    from _customHooks import CustomHooks
    from _discord import DiscordMessage, DiscordRichPresence
    from _image import DetectTemplate
    from _menuing import StartMenu,BagMenu,PickupItems,SaveGame,ResetGame,CatchPokemon,BattleOpponent,IsValidMove,FindEffectiveMove,FleeBattle
    from _stats import GetEncounterLog,GetEncounterRate,GetRNGState,GetShinyLog,GetStats,session_encounters,files
    from _files import WriteFile, ReadFile
    from _catchBlockList import block_schema
    from _navigation import Bonk, FollowPath, PlayerOnMap
    from mmf.bag import GetBag, bag_schema
    from mmf.common import LoadJsonMmap
    from mmf.trainer import trainer_schema, GetTrainer
    from mmf.emu import emu_schema, LangISO, clamp, GetEmu
    from mmf.pokemon import pokemon_schema, natures, hiddenPowers, EnrichMonData, GetOpponent, GetParty
    from mmf.screenshot import GetScreenshot
    from mmf.trainer import trainer_schema, GetTrainer
    from gen3.general import ModeBonk,ModeBunnyHop,ModeCoords,ModeFishing,ModePetalburgLoop,ModePremierBalls,ModeSpin,ModeSweetScent,AutoStop
    from gen3.giftPokemon import CollectGiftMon,ModeBeldum,ModeCastform,ModeFossil,ModeJohtoStarters
    from gen3.legendaries import ModeDeoxysPuzzle,ModeDeoxysResets,ModeGroudon,ModeHoOh,ModeKyogre,ModeLugia,ModeMew,ModeRayquaza,ModeRegis,ModeSouthernIsland
    from gen3.starters import ModeStarters
    from data.mapData import mapRSE
    from data.gameState import GameState
    from data.pokedexGenerator import GenerateDex

    # Set global variables
    ImageFile.LOAD_TRUNCATED_IMAGES = True    
    last_opponent_personality = None
    no_sleep_abilities = ["Shed Skin", "Insomnia", "Vital Spirit"]
    pickup_pokemon = ["Meowth", "Aipom", "Phanpy", "Teddiursa", "Zigzagoon", "Linoone"]

    # File & config variables
    catchBlockListYmlFile = "stats\CatchBlockList.yml"

    # Initialization
    def __init__(self, configFile, botName):
        self.name = botName
        self.isRunning = True
        print('Bot "' + self.name + '" initialised')
        
        # Validate files - Validate the data from the mmf, sometimes it sends junk
        self.bagValidator = fastjsonschema.compile(self.bag_schema)  
        self.EmuValidator = fastjsonschema.compile(self.emu_schema)  
        self.pokemonValidator = fastjsonschema.compile(self.pokemon_schema)  
        self.TrainerValidator = fastjsonschema.compile(self.trainer_schema)

        # Set up the logger
        try:

            LogPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logs'))
            LogFormatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(line:%(lineno)d) %(message)s')
            ConsoleFormatter = logging.Formatter('%(asctime)s - %(message)s')
            LogFile = f"{LogPath}/{self.name}/debug.log"
            print("setting up log  file - " + LogFile)
            os.makedirs(LogPath, exist_ok=True)  # Create logs directory if not exist

            # Set up log file rotation handler
            LogHandler = RotatingFileHandler(LogFile, maxBytes=20 * 1024 * 1024, backupCount=5)
            LogHandler.setFormatter(LogFormatter)
            LogHandler.setLevel(logging.INFO)

            # Set up console log stream handler
            ConsoleHandler = logging.StreamHandler()
            ConsoleHandler.setFormatter(ConsoleFormatter)
            ConsoleHandler.setLevel(logLevel)

            # Create logger and attach handlers
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(LogHandler)
            self.logger.addHandler(ConsoleHandler)
            self.logger.info("Logger set up successfully")
            self.logger.info("Logger mode:" + str(logLevel))
            logging.basicConfig(level=logging.DEBUG)

        except Exception as e:
            print(str(e))
            input("There was an error when setting up the logger - details above, press enter to continue")
            os._exit(1)
        
        # Load the config
        self.config = self.GetConfig(configFile)

        # Validate Python
        try:
            MinMajorVersion = 3
            MinMinorVersion = 10
            MajorVersion = sys.version_info[0]
            MinorVersion = sys.version_info[1]

            if MajorVersion < MinMajorVersion or MinorVersion < MinMinorVersion:
                self.logger.error(
                    f"\n\nPython version is out of date! (Minimum required version for pokebot is "
                    f"{MinMajorVersion}.{MinMinorVersion})\nPlease install the latest version at "
                    f"https://www.python.org/downloads/\n")
                input("Press enter to continue...")
                os._exit(1)

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
            os._exit(1)

        # Validate the Game
        emu = self.GetEmu()
        if any([x in emu["detectedGame"] for x in ["Emerald"]]):  # "Ruby", "Sapphire"
            self.MapDataEnum = self.mapRSE
        # if any([x in emu["detectedGame"] for x in ["FireRed", "LeafGreen"]]):
        #    MapDataEnum = mapFRLG
        else:
            self.logger.error("Unsupported game detected...")
            input("Press enter to continue...")
            os._exit(1)

        # For the _catchBlockList method, set variables and run the checker
        self.BlockListValidator = fastjsonschema.compile(self.block_schema)  # Validate the config file to ensure user didn't do a dumb

        # Create block list file if doesn't exist        
        if not os.path.exists(self.catchBlockListYmlFile):
            self.WriteFile(self.catchBlockListYmlFile, "block_list: []")

        # Load folders
        os.makedirs("stats", exist_ok=True)
        
        # Load in json files
        self.item_list = json.loads(self.ReadFile("S:/30SomethingProgrammer/pokebot-bizhawk/bot/data/items.json"))
        self.location_list = json.loads(self.ReadFile("S:/30SomethingProgrammer/pokebot-bizhawk/bot/data/locations.json"))
        self.move_list = json.loads(self.ReadFile("S:/30SomethingProgrammer/pokebot-bizhawk/bot/data/moves.json"))
        self.pokemon_list = json.loads(self.ReadFile("S:/30SomethingProgrammer/pokebot-bizhawk/bot/data/pokemon.json"))
        self.PokedexList = json.loads(self.ReadFile("S:/30SomethingProgrammer/pokebot-bizhawk/bot/data/pokedex.json"))
        self.type_list = json.loads(self.ReadFile("S:/30SomethingProgrammer/pokebot-bizhawk/bot/data/types.json"))

        # For the inputs method, set variables
        self.input_list_mmap = mmap.mmap(-1, 4096, tagname="bizhawk_input_list-" + self.config["bot_instance_id"],access=mmap.ACCESS_WRITE)
        self.input_list_mmap.seek(0)
        self.hold_input_mmap = mmap.mmap(-1, 4096, tagname="bizhawk_hold_input-" + self.config["bot_instance_id"],access=mmap.ACCESS_WRITE)
        self.hold_input = self.default_input
        self.g_current_index = 1  # Variable that keeps track of what input in the list we are on.
        for i in range(100):  # Clear any prior inputs from last time script ran in case you haven't refreshed in Lua
            self.input_list_mmap.write(bytes('a', encoding="utf-8"))
