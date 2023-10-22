
def ModeStarters(self):
    try:
        starter_choice = self.config["starter"].lower()
        self.logger.info(f"Starter choice: {starter_choice}")
        starter_frames = self.GetRNGState(self.GetTrainer()['tid'], starter_choice)

        if starter_choice not in ["treecko", "torchic", "mudkip"]:
            self.logger.info(f"Unknown starter \"{self.config['starter']}\". Please edit the value in config.yml and restart the "
                     f"script.")
            input("Press enter to continue...")
            self.os._exit(1)

        self.logger.info(f"Soft resetting starter Pokemon...")

        while True:
            self.ReleaseAllInputs()

            # Hammer the A button until we're in the overworld (i.e. into the game and out of the menu)
            while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
                self.PressButton("A")

            # Short delay between A inputs to prevent accidental selection confirmations
            while self.GetTrainer()["state"] == self.GameState.OVERWORLD:
                self.ButtonCombo(["A", 10])

            # Press B to back out of an accidental selection when scrolling to chosen starter
            if starter_choice == "mudkip":
                self.logger.info("Selecting mudkip now")
                while not self.DetectTemplate("mudkip.png"):
                    self.ButtonCombo(["B", "Right"])
            elif starter_choice == "treecko":
                self.logger.info("Selecting treecko now")
                while not self.DetectTemplate("treecko.png"):
                    self.ButtonCombo(["B", "Left"])
            else:
                self.logger.info("Selecting torchic now")

            while True:
                emu = self.GetEmu()
                if emu["rngState"] in starter_frames["rngState"]:
                    self.logger.debug(f"Already rolled on RNG state: {emu['rngState']}, waiting...")
                else:
                    while self.GetTrainer()["state"] == self.GameState.MISC_MENU:
                        self.PressButton("A")

                    starter_frames["rngState"].append(emu["rngState"])
                    self.WriteFile(f"{self.stats_folder}/{self.GetTrainer()['tid']}/{starter_choice}.json",
                              self.json.dumps(starter_frames, indent=4, sort_keys=True))

                    while not self.DetectTemplate("battle/fight.png"):
                        self.PressButton("B")

                        if self.config["mem_hacks"] and self.GetParty()[0]:
                            if self.EncounterPokemon(starter=True):
                                input("Pausing bot for manual intervention. (Don't forget to pause the pokebot.lua "
                                      "script so you can provide inputs). Press Enter to continue...")
                            else:
                                self.ResetGame()
                                break
                    else:
                        if self.GetParty()[0]:
                            if self.EncounterPokemon(starter=True):
                                input("Pausing bot for manual intervention. (Don't forget to pause the pokebot.lua "
                                      "script so you can provide inputs). Press Enter to continue...")
                            else:
                                self.ResetGame()
                                break
                    break
                continue
    except Exception as e:
        self.logger.error(str(e))