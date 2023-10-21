import copy
import os
import json
import math
import time
import pandas as pd
import pydirectinput
from threading import Thread
from datetime import datetime



session_encounters = 0
files = {
    "encounter_log": "stats/encounter_log.json",
    "shiny_log": "stats/shiny_log.json",
    "totals": "stats/totals.json"
}


def GetStats(self):
    try:
        totals = self.ReadFile(files["totals"])
        if totals:
            return json.loads(totals)
        return None
    except Exception as e:
        self.logger.exception(str(e))
        return None


def GetEncounterLog(self):
    default = {"encounter_log": []}
    try:
        encounter_log = self.ReadFile(files["encounter_log"])
        if encounter_log:
            return json.loads(encounter_log)
        return default
    except Exception as e:
        self.logger.exception(str(e))
        return default


def GetShinyLog(self):
    default = {"shiny_log": []}
    try:
        shiny_log = self.ReadFile(files["shiny_log"])
        if shiny_log:
            return json.loads(shiny_log)
        return default
    except Exception as e:
        self.logger.exception(str(e))
        return default


def GetRNGState(self, tid: str, mon: str):
    default = {"rngState": []}
    try:
        file = self.ReadFile(f"stats/{tid}/{mon.lower()}.json")
        data = json.loads(file) if file else default
        return data
    except Exception as e:
        self.logger.exception(str(e))
        return default


def GetEncounterRate(self):
    try:
        fmt = "%Y-%m-%d %H:%M:%S.%f"
        encounter_logs = GetEncounterLog()["encounter_log"]
        if len(encounter_logs) > 1 and session_encounters > 1:
            encounter_rate = int(
                (3600 /
                 (datetime.strptime(encounter_logs[-1]["time_encountered"], fmt) -
                  datetime.strptime(encounter_logs[-min(session_encounters, 250)]["time_encountered"], fmt)
                  ).total_seconds()) * (min(session_encounters, 250)))
            return encounter_rate
        return 0
    except Exception as e:
        self.logger.exception(str(e))
        return 0


def OpponentChanged(self):
    """
    This function checks if there is a different opponent since last check, indicating the game state is probably
    now in a battle
    :return: Boolean value of whether in a battle
    """
    global last_opponent_personality
    try:
        # Fixes a bug where the bot checks the opponent for up to 20 seconds if it was last closed in a battle
        if self.GetTrainer()["state"] == self.GameState.OVERWORLD:
            return False
        
        #recheck again after 5 frames to avoid infinite loop in GetOpponent
        self.WaitFrames(5)
        if self.GetTrainer()["state"] == self.GameState.OVERWORLD:
            return False

        opponent = self.GetOpponent()
        if opponent:
            self.logger.debug(
                f"Checking if opponent's PID has changed... (if {last_opponent_personality} != {opponent['personality']})")
            if last_opponent_personality != opponent["personality"]:
                self.logger.info(
                    f"Opponent has changed! Previous PID: {last_opponent_personality}, New PID: {opponent['personality']}")
                last_opponent_personality = opponent["personality"]
                return True
        return False
    except Exception as e:
        self.logger.exception(str(e))
        return False


def LogEncounter(self, pokemon: dict):
    global session_encounters

    try:
        # Load stats from totals.json file
        stats = self.GetStats()
        # Set up stats file if doesn't exist
        if not stats:
            stats = {}
        if not "pokemon" in stats:
            stats["pokemon"] = {}
        if not "totals" in stats:
            stats["totals"] = {}

        # Set up pokemon stats if first encounter
        if not pokemon["name"] in stats["pokemon"]:
            stats["pokemon"].update({pokemon["name"]: {}})

        # Increment encounters stats
        stats["totals"]["encounters"] = stats["totals"].get("encounters", 0) + 1
        stats["totals"]["phase_encounters"] = stats["totals"].get("phase_encounters", 0) + 1

        # Update Pokémon stats
        stats["pokemon"][pokemon["name"]]["encounters"] = stats["pokemon"][pokemon["name"]].get("encounters", 0) + 1
        stats["pokemon"][pokemon["name"]]["phase_encounters"] = stats["pokemon"][pokemon["name"]].get("phase_encounters", 0) + 1
        stats["pokemon"][pokemon["name"]]["last_encounter_time_unix"] = time.time()
        stats["pokemon"][pokemon["name"]]["last_encounter_time_str"] = str(datetime.now())

        # Pokémon phase highest shiny value
        if not stats["pokemon"][pokemon["name"]].get("phase_highest_sv", None):
            stats["pokemon"][pokemon["name"]]["phase_highest_sv"] = pokemon["shinyValue"]
        else:
            stats["pokemon"][pokemon["name"]]["phase_highest_sv"] = max(pokemon["shinyValue"], stats["pokemon"][pokemon["name"]].get("phase_highest_sv", -1))

        # Pokémon phase lowest shiny value
        if not stats["pokemon"][pokemon["name"]].get("phase_lowest_sv", None):
            stats["pokemon"][pokemon["name"]]["phase_lowest_sv"] = pokemon["shinyValue"]
        else:
            stats["pokemon"][pokemon["name"]]["phase_lowest_sv"] = min(pokemon["shinyValue"], stats["pokemon"][pokemon["name"]].get("phase_lowest_sv", 65536))

        # Pokémon total lowest shiny value
        if not stats["pokemon"][pokemon["name"]].get("total_lowest_sv", None):
            stats["pokemon"][pokemon["name"]]["total_lowest_sv"] = pokemon["shinyValue"]
        else:
            stats["pokemon"][pokemon["name"]]["total_lowest_sv"] = min(pokemon["shinyValue"], stats["pokemon"][pokemon["name"]].get("total_lowest_sv", 65536))

        # Phase highest shiny value
        if not stats["totals"].get("phase_highest_sv", None):
            stats["totals"]["phase_highest_sv"] = pokemon["shinyValue"]
            stats["totals"]["phase_highest_sv_pokemon"] = pokemon["name"]
        elif pokemon["shinyValue"] >= stats["totals"].get("phase_highest_sv", -1):
            stats["totals"]["phase_highest_sv"] = pokemon["shinyValue"]
            stats["totals"]["phase_highest_sv_pokemon"] = pokemon["name"]

        # Phase lowest shiny value
        if not stats["totals"].get("phase_lowest_sv", None):
            stats["totals"]["phase_lowest_sv"] = pokemon["shinyValue"]
            stats["totals"]["phase_lowest_sv_pokemon"] = pokemon["name"]
        elif pokemon["shinyValue"] <= stats["totals"].get("phase_lowest_sv", 65536):
            stats["totals"]["phase_lowest_sv"] = pokemon["shinyValue"]
            stats["totals"]["phase_lowest_sv_pokemon"] = pokemon["name"]

        # Pokémon highest phase IV record
        if not stats["pokemon"][pokemon["name"]].get("phase_highest_iv_sum") or pokemon["IVSum"] >= stats["pokemon"][pokemon["name"]].get("phase_highest_iv_sum", -1):
            stats["pokemon"][pokemon["name"]]["phase_highest_iv_sum"] = pokemon["IVSum"]

        # Pokémon highest total IV record
        if pokemon["IVSum"] >= stats["pokemon"][pokemon["name"]].get("total_highest_iv_sum", -1):
            stats["pokemon"][pokemon["name"]]["total_highest_iv_sum"] = pokemon["IVSum"]

        # Pokémon lowest phase IV record
        if not stats["pokemon"][pokemon["name"]].get("phase_lowest_iv_sum") or pokemon["IVSum"] <= stats["pokemon"][pokemon["name"]].get("phase_lowest_iv_sum", 999):
            stats["pokemon"][pokemon["name"]]["phase_lowest_iv_sum"] = pokemon["IVSum"]

        # Pokémon lowest total IV record
        if pokemon["IVSum"] <= stats["pokemon"][pokemon["name"]].get("total_lowest_iv_sum", 999):
            stats["pokemon"][pokemon["name"]]["total_lowest_iv_sum"] = pokemon["IVSum"]

        # Phase highest IV sum record
        if not stats["totals"].get("phase_highest_iv_sum") or pokemon["IVSum"] >= stats["totals"].get("phase_highest_iv_sum", -1):
            stats["totals"]["phase_highest_iv_sum"] = pokemon["IVSum"]
            stats["totals"]["phase_highest_iv_sum_pokemon"] = pokemon["name"]

        # Phase lowest IV sum record
        if not stats["totals"].get("phase_lowest_iv_sum") or pokemon["IVSum"] <= stats["totals"].get("phase_lowest_iv_sum", 999):
            stats["totals"]["phase_lowest_iv_sum"] = pokemon["IVSum"]
            stats["totals"]["phase_lowest_iv_sum_pokemon"] = pokemon["name"]

        # Total highest IV sum record
        if pokemon["IVSum"] >= stats["totals"].get("highest_iv_sum", -1):
            stats["totals"]["highest_iv_sum"] = pokemon["IVSum"]
            stats["totals"]["highest_iv_sum_pokemon"] = pokemon["name"]

        # Total lowest IV sum record
        if pokemon["IVSum"] <= stats["totals"].get("lowest_iv_sum", 999):
            stats["totals"]["lowest_iv_sum"] = pokemon["IVSum"]
            stats["totals"]["lowest_iv_sum_pokemon"] = pokemon["name"]

        if self.self.config["log"]:
            # Log all encounters to a CSV file per phase
            csvpath = "stats/encounters/"
            csvfile = "Phase {} Encounters.csv".format(stats["totals"].get("shiny_encounters", 0))
            pokemondata = pd.DataFrame.from_dict(pokemon, orient="index").drop(["enrichedMoves", "moves", "pp", "type"]).sort_index().transpose()
            os.makedirs(csvpath, exist_ok=True)
            header = False if os.path.exists(f"{csvpath}{csvfile}") else True
            pokemondata.to_csv(f"{csvpath}{csvfile}", mode="a", encoding="utf-8", index=False, header=header)

        encounter_log = GetEncounterLog()

        # Pokémon shiny average
        if stats["pokemon"][pokemon["name"]].get("shiny_encounters"):
            avg = int(math.floor(stats["pokemon"][pokemon["name"]]["encounters"] / stats["pokemon"][pokemon["name"]]["shiny_encounters"]))
            stats["pokemon"][pokemon["name"]]["shiny_average"] = f"1/{avg:,}"

        # Total shiny average
        if stats["totals"].get("shiny_encounters"):
            avg = int(math.floor(stats["totals"]["encounters"] / stats["totals"]["shiny_encounters"]))
            stats["totals"]["shiny_average"] = f"1/{avg:,}"

        # Log encounter to encounter_log
        log_obj = {
            "time_encountered": str(datetime.now()),
            "pokemon_obj": pokemon,
            "snapshot_stats": {
                "phase_encounters": stats["totals"]["phase_encounters"],
                "species_encounters": stats["pokemon"][pokemon["name"]]["encounters"],
                "species_shiny_encounters": stats["pokemon"][pokemon["name"]].get("shiny_encounters", 0),
                "total_encounters": stats["totals"]["encounters"],
                "total_shiny_encounters": stats["totals"].get("shiny_encounters", 0),
            }
        }
        encounter_log["encounter_log"].append(log_obj)
        encounter_log["encounter_log"] = encounter_log["encounter_log"][-250:]
        self.WriteFile(files["encounter_log"], json.dumps(encounter_log, indent=4, sort_keys=True))
        if pokemon["shiny"]:
            shiny_log = GetShinyLog()
            shiny_log["shiny_log"].append(log_obj)
            self.WriteFile(files["shiny_log"], json.dumps(shiny_log, indent=4, sort_keys=True))

        # Same Pokémon encounter streak records
        if len(encounter_log["encounter_log"]) > 1 and encounter_log["encounter_log"][-2]["pokemon_obj"]["name"] == pokemon["name"]:
            stats["totals"]["current_streak"] = stats["totals"].get("current_streak", 0) + 1
        else:
            stats["totals"]["current_streak"] = 1
        if stats["totals"].get("current_streak", 0) >= stats["totals"].get("phase_streak", 0):
            stats["totals"]["phase_streak"] = stats["totals"].get("current_streak", 0)
            stats["totals"]["phase_streak_pokemon"] = pokemon["name"]

        if pokemon["shiny"]:
            stats["pokemon"][pokemon["name"]]["shiny_encounters"] = stats["pokemon"][pokemon["name"]].get("shiny_encounters", 0) + 1
            stats["totals"]["shiny_encounters"] = stats["totals"].get("shiny_encounters", 0) + 1

        self.logger.info(f"------------------ {pokemon['name']} ------------------")
        article = "an" if pokemon["name"].lower()[0] in {"a", "e", "i", "o", "u"} else "a"
        self.logger.info("Encountered {} {} at {}".format(
            article,
            pokemon['name'],
            pokemon['metLocationName']))
        self.logger.info("HP: {} | ATK: {} | DEF: {} | SPATK: {} | SPDEF: {} | SPE: {}".format(
            pokemon['hpIV'],
            pokemon['attackIV'],
            pokemon['defenseIV'],
            pokemon['spAttackIV'],
            pokemon['spDefenseIV'],
            pokemon['speedIV']))
        self.logger.info("Shiny Value (SV): {:,} (is {:,} < 8 = {})".format(
            pokemon['shinyValue'],
            pokemon['shinyValue'],
            pokemon['shiny']))
        self.logger.info("Phase encounters: {} | {} Phase Encounters: {}".format(
            stats["totals"]["phase_encounters"],
            pokemon["name"],
            stats["pokemon"][pokemon["name"]]["phase_encounters"]))
        self.logger.info("{} Encounters: {:,} | Lowest {} SV seen this phase: {}".format(
            pokemon["name"],
            stats["pokemon"][pokemon["name"]]["encounters"],
            pokemon["name"],
            stats["pokemon"][pokemon["name"]]["phase_lowest_sv"]))
        self.logger.info("Shiny {} Encounters: {:,} | {} Shiny Average: {}".format(
            pokemon["name"],
            stats["pokemon"][pokemon["name"]].get("shiny_encounters", 0),
            pokemon["name"],
            stats["pokemon"][pokemon["name"]].get("shiny_average", 0)))
        self.logger.info("Total Encounters: {:,} | Total Shiny Encounters: {:,} | Total Shiny Average: {}".format(
            stats["totals"]["encounters"],
            stats["totals"].get("shiny_encounters", 0),
            stats["totals"].get("shiny_average", 0)))
        self.logger.info(f"--------------------------------------------------")

        if pokemon["shiny"]:
            time.sleep(self.config["misc"].get("shiny_delay", 0))
        if self.config["misc"]["obs"].get("enable_screenshot", None) and \
        pokemon["shiny"]:
            # Throw out Pokemon for screenshot
            while self.GetTrainer()["state"] != self.GameState.BATTLE:
                self.PressButton("B")
            self.WaitFrames(180)
            for key in self.config["misc"]["obs"]["hotkey_screenshot"]:
                pydirectinput.keyDown(key)
            for key in reversed(self.config["misc"]["obs"]["hotkey_screenshot"]):
                pydirectinput.keyUp(key)

        # Run custom code in CustomHooks in a thread
        hook = (copy.deepcopy(pokemon), copy.deepcopy(stats))
        Thread(target=self.CustomHooks, args=(hook,)).start()

        if pokemon["shiny"]:
            # Total longest phase
            if stats["totals"]["phase_encounters"] > stats["totals"].get("longest_phase_encounters", 0):
                stats["totals"]["longest_phase_encounters"] = stats["totals"]["phase_encounters"]
                stats["totals"]["longest_phase_pokemon"] = pokemon["name"]

            # Total shortest phase
            if not stats["totals"].get("shortest_phase_encounters", None) or \
                stats["totals"]["phase_encounters"] <= stats["totals"]["shortest_phase_encounters"]:
                stats["totals"]["shortest_phase_encounters"] = stats["totals"]["phase_encounters"]
                stats["totals"]["shortest_phase_pokemon"] = pokemon["name"]

            # Reset phase stats
            stats["totals"].pop("phase_encounters", None)
            stats["totals"].pop("phase_highest_sv", None)
            stats["totals"].pop("phase_highest_sv_pokemon", None)
            stats["totals"].pop("phase_lowest_sv", None)
            stats["totals"].pop("phase_lowest_sv_pokemon", None)
            stats["totals"].pop("phase_highest_iv_sum", None)
            stats["totals"].pop("phase_highest_iv_sum_pokemon", None)
            stats["totals"].pop("phase_lowest_iv_sum", None)
            stats["totals"].pop("phase_lowest_iv_sum_pokemon", None)
            stats["totals"].pop("current_streak", None)
            stats["totals"].pop("phase_streak", None)
            stats["totals"].pop("phase_streak_pokemon", None)

            # Reset Pokémon phase stats
            for pokemon["name"] in stats["pokemon"]:
                stats["pokemon"][pokemon["name"]].pop("phase_encounters", None)
                stats["pokemon"][pokemon["name"]].pop("phase_highest_sv", None)
                stats["pokemon"][pokemon["name"]].pop("phase_lowest_sv", None)
                stats["pokemon"][pokemon["name"]].pop("phase_highest_iv_sum", None)
                stats["pokemon"][pokemon["name"]].pop("phase_lowest_iv_sum", None)

        # Save stats file
        self.WriteFile(files["totals"], json.dumps(stats, indent=4, sort_keys=True))
        session_encounters += 1

        # Backup stats folder every n encounters
        if self.config["backup_stats"] > 0 and \
        stats["totals"].get("encounters", None) and \
        stats["totals"]["encounters"] % self.config["backup_stats"] == 0:
            self.BackupFolder("./stats/", "./backups/stats-{}.zip".format(time.strftime("%Y%m%d-%H%M%S")))

    except Exception as e:
        self.logger.exception(str(e))
        return False


def EncounterPokemon(self, starter: bool = False):
    """
    New Pokémon encountered, record stats + decide whether to catch/battle/flee
    :param starter: Boolean value of whether in starter mode
    :return: Boolean value of whether in battle
    """
    legendary_hunt = self.config["bot_mode"] in ["manual", "rayquaza", "kyogre", "groudon", "southern island", "regis",
                                            "deoxys resets", "deoxys runaways", "mew"]

    self.logger.info("Identifying Pokemon...")
    self.ReleaseAllInputs()

    if starter:
        self.WaitFrames(30)

    if self.GetTrainer()["state"] == self.GameState.OVERWORLD:
        return False

    pokemon = self.GetParty()[0] if starter else self.GetOpponent()
    LogEncounter(pokemon)

    replace_battler = False

    if pokemon["shiny"]:
        if not starter and not legendary_hunt and self.config["catch_shinies"]:
            blocked = self.GetBlockList()
            opponent = self.GetOpponent()
            if opponent["name"] in blocked["block_list"]:
                self.logger.info("---- Pokemon is in list of non-catpures. Fleeing battle ----")
                if self.config["discord"]["messages"]:
                    try:
                        content = f"Encountered shiny {opponent['name']}... but catching this species is disabled. Fleeing battle!"
                        webhook = self.DiscordWebhook(url=self.config["discord"]["webhook_url"], content=content)
                        webhook.execute()
                    except Exception as e:
                        self.logger.exception(str(e))
                        pass
                self.FleeBattle()
            else: 
                self.CatchPokemon()
        elif legendary_hunt:
            input("Pausing bot for manual intervention. (Don't forget to pause the pokebot.lua script so you can "
                  "provide inputs). Press Enter to continue...")
        elif not self.config["catch_shinies"]:
            self.FleeBattle()
        return True
    else:
        if self.config["bot_mode"] == "manual":
            while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
                self.WaitFrames(100)
        elif starter:
            return False

        if self.CustomCatchselfConfig(pokemon):
            self.CatchPokemon()

        if not legendary_hunt:
            if self.config["battle"]:
                battle_won = self.BattleOpponent()
                replace_battler = not battle_won
            else:
                self.FleeBattle()
        elif self.config["bot_mode"] == "deoxys resets":
            if not self.config["mem_hacks"]:
                # Wait until sprite has appeared in battle before reset
                self.WaitFrames(240)
            self.ResetGame()
            return False
        else:
            self.FleeBattle()

        if self.config["pickup"] and not legendary_hunt:
            self.PickupItems()

        # If total encounters modulo self.config["save_every_x_encounters"] is 0, save the game
        # Save every x encounters to prevent data loss (pickup, levels etc)
        stats = GetStats()
        if self.config["autosave_encounters"] > 0 and stats["totals"]["encounters"] > 0 and \
                stats["totals"]["encounters"] % self.config["autosave_encounters"] == 0:
            self.SaveGame()

        if replace_battler:
            if not self.config["cycle_lead_pokemon"]:
                self.logger.info("Lead Pokemon can no longer battle. Ending the script!")
                self.FleeBattle()
                return False
            else:
                self.StartMenu("pokemon")

                # Find another healthy battler
                party_pp = [0, 0, 0, 0, 0, 0]
                for i, mon in enumerate(self.GetParty()):
                    if mon is None:
                        continue

                    if mon["hp"] > 0 and i != 0:
                        for j, move in enumerate(mon["enrichedMoves"]):
                            if self.IsValidMove(move) and mon["pp"][j] > 0:
                                party_pp[i] += move["pp"]

                highest_pp = max(party_pp)
                lead_idx = party_pp.index(highest_pp)

                if highest_pp == 0:
                    self.logger.info("Ran out of Pokemon to battle with. Ending the script!")
                    os._exit(1)

                lead = self.GetParty()[lead_idx]
                if lead is not None:
                    self.logger.info(f"Replacing lead battler with {lead['name']} (Party slot {lead_idx})")

                self.PressButton("A")
                self.WaitFrames(60)
                self.PressButton("A")
                self.WaitFrames(15)

                for _ in range(3):
                    self.PressButton("Up")
                    self.WaitFrames(15)

                self.PressButton("A")
                self.WaitFrames(15)

                for _ in range(lead_idx):
                    self.PressButton("Down")
                    self.WaitFrames(15)

                # Select target Pokémon and close out menu
                self.PressButton("A")
                self.WaitFrames(60)

                self.logger.info("Replaced lead Pokemon!")

                for _ in range(5):
                    self.self.PressButton("B")
                    self.WaitFrames(15)
        return False
