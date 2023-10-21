import json
import os


def CollectGiftMon(self, target: str):
    rng_frames = self.GetRNGState(self.GetTrainer()["tid"], target)
    party_size = self.len(self.GetParty())

    if party_size == 6:
        self.logger.info("Please leave at least one party slot open, then restart the script.")
        os._exit(1)

    while True:
        # Button mash through intro/title
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.PressButton("A")
            self.WaitFrames(8)

        # Text goes faster with B held
        self.HoldButton("B")

        emu = self.GetEmu()
        while len(self.GetParty()) == party_size:
            emu = self.GetEmu()
            if emu["rngState"] in rng_frames:
                self.logger.debug(f"Already rolled on RNG state: {emu['rngState']}, waiting...")
                continue
            self.PressButton("A")
            self.WaitFrames(5)

        rng_frames["rngState"].append(emu["rngState"])
        self.WriteFile(f"stats/{self.GetTrainer()['tid']}/{target.lower()}.json",
                  json.dumps(rng_frames, indent=4, sort_keys=True))

        mon = self.GetParty()[party_size]

        # Open the menu and find Gift mon in party
        self.ReleaseButton("B")

        if self.config["mem_hacks"] and not mon["shiny"]:
            self.LogEncounter(mon)
            self.HoldButton("Power")
            self.WaitFrames(60)
            self.ReleaseButton("Power")
            continue

        while not self.DetectTemplate("start_menu/select.png"):
            self.PressButton("B")

            for _ in range(4):
                if self.DetectTemplate("start_menu/select.png"):
                    break
                self.WaitFrames(1)

        while self.DetectTemplate("start_menu/select.png"):
            self.PressButton("B")

            for _ in range(4):
                if not self.DetectTemplate("start_menu/select.png"):
                    break
                self.WaitFrames(1)

        self.StartMenu("pokemon")

        self.WaitFrames(60)

        for _ in range(party_size):
            self.ButtonCombo(["Down", 15])

        self.ButtonCombo(["A", 15, "A", 60])

        self.LogEncounter(mon)

        if not mon["shiny"]:
            self.HoldButton("Power")
            self.WaitFrames(60)
            self.ReleaseButton("Power")
        else:
            input("Pausing bot for manual intervention. (Don't forget to pause the pokebot.lua script so you can "
                  "provide inputs). Press Enter to continue...")


def ModeBeldum(self):
    trainer = self.GetTrainer()
    x, y = trainer["posX"], trainer["posY"]

    if not self.PlayerOnMap(self.MapDataEnum.MOSSDEEP_CITY_H.value) or not ((x == 3 and y == 3) or (x == 4 and y == 2)):
        self.logger.info("Please face the player toward the Pokeball in Steven's house after saving the game, then restart the "
                 "script.")
        os._exit(1)

    CollectGiftMon("Beldum")


def ModeCastform(self):
    trainer = self.GetTrainer()
    x, y = trainer["posX"], trainer["posY"]

    if (not self.PlayerOnMap(self.MapDataEnum.ROUTE_119_B.value) or not (
            (x == 2 and y == 3) or (x == 3 and y == 2) or (x == 1 and y == 2))):
        self.logger.info("Please face the player toward the scientist after saving the game, then restart the script.")
        os._exit(1)

    CollectGiftMon("Castform")


def ModeFossil(self):
    trainer = self.GetTrainer()
    x, y = trainer["posX"], trainer["posY"]

    if not self.PlayerOnMap(self.MapDataEnum.RUSTBORO_CITY_B.value) or y != 8 and not (x == 13 or x == 15):
        self.logger.info("Please face the player toward the Fossil researcher after handing it over, re-entering the room, "
                 "and saving the game. Then restart the script.")
        os._exit(1)

    CollectGiftMon(self.config["fossil"])


def ModeJohtoStarters(self):
    trainer = self.GetTrainer()
    x, y = trainer["posX"], trainer["posY"]

    if not self.PlayerOnMap(self.MapDataEnum.LITTLEROOT_TOWN_E.value) or not (y == 5 and 8 <= x <= 10):
        self.logger.info("Please face the player toward a Pokeball in Birch's Lab after saving the game, then restart the "
                 "script.")
        os._exit(1)

    CollectGiftMon(self.config["johto_starter"])
