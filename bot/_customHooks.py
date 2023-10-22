# A method of class Bot - derived from __init__
import os

def CustomHooks(self, hook):
    """
    This function is called every time an encounter is logged, but before phase stats are reset (if shiny)
    this file is useful for custom webhooks or logging to external databases if you understand Python

    Note: this function runs in a thread and will not hold up the bot if you need to run any slow hooks
    """
    try:
        # Deep copy of pokemon and stats dictionaries when the thread was called to avoid main thread overwriting vars
        pokemon = hook[0]
        stats = hook[1]

        ### Your custom code goes here ###

    except Exception as e:
        self.logger.exception(str(e))
        self.logger.error("Failed to run custom hooks...")

    try:
        # Discord messages
        if self.config["discord"]["messages"]:
            # Formatted IV table
            if self.config["discord"]["iv_format"] == "formatted":
                iv_field = "```" \
                           "╔═══╤═══╤═══╤═══╤═══╤═══╗\n" \
                           "║HP │ATK│DEF│SPA│SPD│SPE║\n" \
                           "╠═══╪═══╪═══╪═══╪═══╪═══╣\n" \
                           "║{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}║\n" \
                           "╚═══╧═══╧═══╧═══╧═══╧═══╝" \
                           "```".format(
                    pokemon["hpIV"],
                    pokemon["attackIV"],
                    pokemon["defenseIV"],
                    pokemon["spAttackIV"],
                    pokemon["spDefenseIV"],
                    pokemon["speedIV"])
            else:
                # Default to basic IV formatting
                iv_field = "HP: {} | ATK: {} | DEF: {} | SPATK: {} | SPDEF: {} | SPE: {}".format(
                    pokemon["hpIV"],
                    pokemon["attackIV"],
                    pokemon["defenseIV"],
                    pokemon["spAttackIV"],
                    pokemon["spDefenseIV"],
                    pokemon["speedIV"])

            try:
                # Discord shiny Pokémon encountered
                if self.config["discord"]["shiny_pokemon_encounter"]["enable"] and pokemon["shiny"]:
                    # Discord pings
                    discord_ping = ""
                    match self.config["discord"]["shiny_pokemon_encounter"]["ping_mode"]:
                        case "role":
                            discord_ping = "📢 <@&{}>".format(self.config["discord"]["shiny_pokemon_encounter"]["ping_id"])
                        case "user":
                            discord_ping = "📢 <@{}>".format(self.config["discord"]["shiny_pokemon_encounter"]["ping_id"])
                    self.DiscordMessage(
                        webhook_url=self.config["discord"]["shiny_pokemon_encounter"].get("webhook_url", None),
                        content="Encountered a shiny ✨{}✨!\n{}".format(
                                pokemon["name"],
                                discord_ping
                        ),
                        embed=True,
                        embed_title="Shiny encountered!",
                        embed_description="{} {} (Lv. {:,}) at {}!".format(
                                        pokemon["nature"],
                                        pokemon["name"],
                                        pokemon["level"],
                                        pokemon["metLocationName"]),
                        embed_fields={
                            "Shiny Value": "{:,}".format(pokemon["shinyValue"]),
                            "IVs": iv_field,
                            "{} Encounters".format(
                                            pokemon["name"]): "{:,} ({:,}✨)".format(
                                            stats["pokemon"][pokemon["name"]].get("encounters", 0),
                                            stats["pokemon"][pokemon["name"]].get("shiny_encounters", 0)),
                            "{} Phase Encounters".format(
                                            pokemon["name"]): "{:,}".format(
                                            stats["pokemon"][pokemon["name"]].get("phase_encounters", 0)),
                            "Phase Encounters": "{:,} ({:,}/h)".format(
                                            stats["totals"].get("phase_encounters", 0),
                                            self.GetEncounterRate()),
                            "Phase IV Sum Records": ":arrow_up: `{:,}` IV {}\n:arrow_down: `{:,}` IV {}".format(
                                            stats["totals"].get("phase_highest_iv_sum", 0),
                                            stats["totals"].get("phase_highest_iv_sum_pokemon", "N/A"),
                                            stats["totals"].get("phase_lowest_iv_sum", 0),
                                            stats["totals"].get("phase_lowest_iv_sum_pokemon", "N/A")),
                            "Phase SV Records": ":arrow_up: `{:,}` SV {}\n:arrow_down: `{:,}` SV ✨{}✨".format(
                                            stats["totals"].get("phase_highest_sv", 0),
                                            stats["totals"].get("phase_highest_sv_pokemon", "N/A"),
                                            stats["totals"].get("phase_lowest_sv", 0),
                                            stats["totals"].get("phase_lowest_sv_pokemon", "N/A")),
                            "Phase Same Pokémon Streak": "{:,} {} were encountered in a row!".format(
                                            stats["totals"].get("phase_streak", 0),
                                            stats["totals"].get("phase_streak_pokemon", "N/A")),
                            "Total Encounters": "{:,} ({:,}✨)".format(
                                            stats["totals"].get("encounters", 0),
                                            stats["totals"].get("shiny_encounters", 0))},
                        embed_thumbnail=(self.interface_folder+"./modules/interface/sprites/pokemon/shiny/{}.png").format(
                                            pokemon["name"]),
                        embed_footer=f"PokéBot ID: {self.config['profile']}",
                        embed_color="ffd242")
            except Exception as e:
                self.logger.exception(str(e))

            try:
                # Discord Pokémon encounter milestones
                if self.config["discord"]["pokemon_encounter_milestones"]["enable"] and \
                stats["pokemon"][pokemon["name"]].get("encounters", -1) % self.config["discord"]["pokemon_encounter_milestones"].get("interval", 0) == 0:
                    # Discord pings
                    discord_ping = ""
                    match self.config["discord"]["pokemon_encounter_milestones"]["ping_mode"]:
                        case "role":
                            discord_ping = "📢 <@&{}>".format(self.config["discord"]["pokemon_encounter_milestones"]["ping_id"])
                        case "user":
                            discord_ping = "📢 <@{}>".format(self.config["discord"]["pokemon_encounter_milestones"]["ping_id"])
                    self.DiscordMessage(
                        webhook_url=self.config["discord"]["pokemon_encounter_milestones"].get("webhook_url", None),
                        content=f"🎉 New milestone achieved!\n{discord_ping}",
                        embed=True,
                        embed_description="{:,} {} encounters!".format(
                                        stats["pokemon"][pokemon["name"]].get("encounters", 0),
                                        pokemon["name"]),
                        embed_thumbnail="./modules/interface/sprites/pokemon/{}.png".format(
                                        pokemon["name"]),
                        embed_footer=f"PokéBot ID: {self.config['profile']}",
                        embed_color="50C878")
            except Exception as e:
                self.logger.exception(str(e))

            try:
                # Discord shiny Pokémon encounter milestones
                if self.config["discord"]["shiny_pokemon_encounter_milestones"]["enable"] and \
                pokemon["shiny"] and \
                stats["pokemon"][pokemon["name"]].get("shiny_encounters", -1) % self.config["discord"]["shiny_pokemon_encounter_milestones"].get("interval", 0) == 0:
                    # Discord pings
                    discord_ping = ""
                    match self.config["discord"]["shiny_pokemon_encounter_milestones"]["ping_mode"]:
                        case "role":
                            discord_ping = "📢 <@&{}>".format(self.config["discord"]["shiny_pokemon_encounter_milestones"]["ping_id"])
                        case "user":
                            discord_ping = "📢 <@{}>".format(self.config["discord"]["shiny_pokemon_encounter_milestones"]["ping_id"])
                    self.DiscordMessage(
                        webhook_url=self.config["discord"]["shiny_pokemon_encounter_milestones"].get("webhook_url", None),
                        content=f"🎉 New milestone achieved!\n{discord_ping}",
                        embed=True,
                        embed_description="{:,} shiny ✨{}✨ encounters!".format(
                                            stats["pokemon"][pokemon["name"]].get("shiny_encounters", 0),
                                            pokemon["name"]),
                        embed_thumbnail="./modules/interface/sprites/pokemon/shiny/{}.png".format(
                                            pokemon["name"]),
                        embed_footer=f"PokéBot ID: {self.config['profile']}",
                        embed_color="ffd242")
            except Exception as e:
                self.logger.exception(str(e))

            try:
                # Discord total encounter milestones
                if self.config["discord"]["total_encounter_milestones"]["enable"] and \
                stats["totals"].get("encounters", -1) % self.config["discord"]["total_encounter_milestones"].get("interval", 0) == 0:
                    # Discord pings
                    discord_ping = ""
                    match self.config["discord"]["total_encounter_milestones"]["ping_mode"]:
                        case "role":
                            discord_ping = "📢 <@&{}>".format(self.config["discord"]["total_encounter_milestones"]["ping_id"])
                        case "user":
                            discord_ping = "📢 <@{}>".format(self.config["discord"]["total_encounter_milestones"]["ping_id"])
                    self.DiscordMessage(
                        webhook_url=self.config["discord"]["total_encounter_milestones"].get("webhook_url", None),
                        content=f"🎉 New milestone achieved!\n{discord_ping}",
                        embed=True,
                        embed_description="{:,} total encounters!".format(
                                          stats["totals"].get("encounters", 0)),
                        embed_thumbnail=(self.interface_folder+"/sprites/items/{}.png").format(
                            self.random.choice([
                                "Dive Ball",
                                "Great Ball",
                                "Light Ball",
                                "Luxury Ball",
                                "Master Ball",
                                "Nest Ball",
                                "Net Ball",
                                "Poké Ball",
                                "Premier Ball",
                                "Repeat Ball",
                                "Safari Ball",
                                "Smoke Ball",
                                "Timer Ball",
                                "Ultra Ball"])),
                        embed_footer=f"PokéBot ID: {self.config['profile']}",
                        embed_color="50C878")
            except Exception as e:
                self.logger.exception(str(e))

            try:
                # Discord phase encounter notifications
                if self.config["discord"]["phase_summary"]["enable"] and \
                not pokemon["shiny"] and \
                (stats["totals"].get("phase_encounters", -1) == self.config["discord"]["phase_summary"].get("first_interval", 0) or
                (stats["totals"].get("phase_encounters", -1) > self.config["discord"]["phase_summary"].get("first_interval", 0) and
                stats["totals"].get("phase_encounters", -1) % self.config["discord"]["phase_summary"].get("consequent_interval", 0) == 0)):
                    # Discord pings
                    discord_ping = ""
                    match self.config["discord"]["phase_summary"]["ping_mode"]:
                        case "role":
                            discord_ping = "📢 <@&{}>".format(self.config["discord"]["phase_summary"]["ping_id"])
                        case "user":
                            discord_ping = "📢 <@{}>".format(self.config["discord"]["phase_summary"]["ping_id"])
                    self.DiscordMessage(
                        webhook_url=self.config["discord"]["phase_summary"].get("webhook_url", None),
                        content="💀 The current phase has reached {:,} encounters!\n{}".format(
                                stats["totals"].get("phase_encounters", 0),
                                discord_ping),
                        embed=True,
                        embed_fields={
                            "Phase Encounters": "{:,} ({:,}/h)".format(
                                                    stats["totals"].get("phase_encounters", 0),
                                                    self.GetEncounterRate()),
                            "Phase IV Sum Records": ":arrow_up: IV `{:,}` {}\n:arrow_down: IV `{:,}` {}".format(
                                                    stats["totals"].get("phase_highest_iv_sum", 0),
                                                    stats["totals"].get("phase_highest_iv_sum_pokemon", "N/A"),
                                                    stats["totals"].get("phase_lowest_iv_sum", 0),
                                                    stats["totals"].get("phase_lowest_iv_sum_pokemon", "N/A")),
                            "Phase SV Records": ":arrow_up: SV `{:,}` {}\n:arrow_down: SV `{:,}` {}".format(
                                                    stats["totals"].get("phase_highest_sv", 0),
                                                    stats["totals"].get("phase_highest_sv_pokemon", "N/A"),
                                                    stats["totals"].get("phase_lowest_sv", 0),
                                                    stats["totals"].get("phase_lowest_sv_pokemon", "N/A")),
                            "Phase Same Pokémon Streak": "{:,} {} were encountered in a row!".format(
                                                    stats["totals"].get("phase_streak", 0),
                                                    stats["totals"].get("phase_streak_pokemon", "N/A")),
                            "Total Encounters": "{:,} ({:,}✨)".format(
                                                    stats["totals"].get("encounters", 0),
                                                    stats["totals"].get("shiny_encounters", 0))},
                        embed_footer=f"PokéBot ID: {self.config['profile']}",
                        embed_color="D70040")
            except Exception as e:
                self.logger.exception(str(e))
    except Exception as e:
        self.logger.exception(str(e))

    try:
        # Post the most recent OBS stream screenshot to Discord
        # (screenshot is taken in Stats.py before phase resets)
        if self.config["misc"]["obs"].get("webhook_url", None) and pokemon["shiny"]:
            def DiscordScreenshot():
                self.time.sleep(3) # Give the screenshot some time to save to disk
                images = self.glob.glob("{}*.png".format(self.config["misc"]["obs"]["replay_dir"]))
                image = max(images, key=os.path.getctime)
                self.DiscordMessage(
                    webhook_url=self.config["misc"]["obs"].get("webhook_url", None),
                    image=image)
            # Run in a thread to not hold up other messages
            self.Thread(target=DiscordScreenshot).start()
    except Exception as e:
        self.logger.exception(str(e))

    try:
        # Save OBS replay buffer n seconds after encountering a shiny
        if self.config["misc"]["obs"]["enable_replay_buffer"] and pokemon["shiny"]:
            def ReplayBuffer():
                self.time.sleep(self.config["misc"]["obs"].get("replay_buffer_delay", 0))
                for key in self.config["misc"]["obs"]["hotkey_replay_buffer"]:
                    self.pydirectinput.keyDown(key)
                for key in reversed(self.config["misc"]["obs"]["hotkey_replay_buffer"]):
                    self.pydirectinput.keyUp(key)
            # Run in a thread to not hold up other messages
            self.Thread(target=ReplayBuffer).start()
    except Exception as e:
        self.logger.exception(str(e))