import json
import logging
import os


def ModeGroudon(self):
    trainer = self.GetTrainer()
    if (not self.PlayerOnMap(self.MapDataEnum.TERRA_CAVE_A.value) or
            not 11 <= trainer["posX"] <= 20 and 26 <= trainer["posY"] <= 27):
        self.logger.info("Please place the player below Groudon in Terra Cave and restart the script.")
        os._exit(1)

    while True:
        self.FollowPath([(17, 26)])

        self.EncounterPokemon()

        # Exit and re-enter
        self.FollowPath([
            (7, 26),
            (7, 15),
            (9, 15),
            (9, 4),
            (5, 4),
            (5, 99, self.MapDataEnum.TERRA_CAVE.value),
            (14, -99, self.MapDataEnum.TERRA_CAVE_A.value),
            (9, 4), (9, 15),
            (7, 15),
            (7, 26),
            (11, 26)
        ])


def ModeKyogre(self):
    trainer = self.GetTrainer()
    if (not self.PlayerOnMap(self.MapDataEnum.MARINE_CAVE_A.value) or
            not 5 <= trainer["posX"] <= 14 and 26 <= trainer["posY"] <= 27):
        self.logger.info("Please place the player below Kyogre in Marine Cave and restart the script.")
        os._exit(1)

    while True:
        self.FollowPath([(9, 26)])

        self.EncounterPokemon()

        # Exit and re-enter
        self.FollowPath([
            (9, 27),
            (18, 27),
            (18, 14),
            (14, 14),
            (14, 4),
            (20, 4),
            (20, 99, self.MapDataEnum.MARINE_CAVE.value),
            (14, -99, self.MapDataEnum.MARINE_CAVE_A.value),
            (14, 4),
            (14, 14),
            (18, 14),
            (18, 27),
            (14, 27)
        ])


def ModeRayquaza(self):
    trainer = self.GetTrainer()
    if (not self.PlayerOnMap(self.MapDataEnum.SKY_PILLAR_G.value) or
            not (trainer["posX"] == 14 and trainer["posY"] <= 12)):
        self.logger.info("Please place the player below Rayquaza at the Sky Pillar and restart the script.")
        os._exit(1)

    while True:
        while not self.OpponentChanged():
            self.ButtonCombo(["A", "Up"])  # Walk up toward Rayquaza while mashing A

        self.EncounterPokemon()

        # Wait until battle is over
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.WaitFrames(1)
            continue

        # Exit and re-enter
        self.PressButton("B")
        self.FollowPath([
            (14, 11),
            (12, 11),
            (12, 15),
            (16, 15),
            (16, -99, self.MapDataEnum.SKY_PILLAR_F.value),
            (10, -99, self.MapDataEnum.SKY_PILLAR_G.value),
            (12, 15),
            (12, 11),
            (14, 11),
            (14, 7)
        ])


def ModeMew(self):
    trainer = self.GetTrainer()
    if (not self.PlayerOnMap(self.MapDataEnum.FARAWAY_ISLAND.value) or not (
            22 <= trainer["posX"] <= 23 and 8 <= trainer["posY"] <= 10)):
        self.logger.info("Please place the player below the entrance to Mew's area, then restart the script.")
        os._exit(1)
        return

    while True:
        # Enter main area
        while self.PlayerOnMap(self.MapDataEnum.FARAWAY_ISLAND.value):
            self.FollowPath([
                (22, 8),
                (22, -99, self.MapDataEnum.FARAWAY_ISLAND_A.value)
            ])

        self.WaitFrames(30)
        self.HoldButton("B")

        self.FollowPath([
            (self.GetTrainer()["posX"], 16),
            (16, 16)
        ])
        # 
        # Follow Mew up while mashing A
        self.HoldButton("Up")

        while not self.OpponentChanged():
            self.ButtonCombo(["A", 8])

        self.EncounterPokemon()

        for _ in range(6):
            self.PressButton("B")
            self.WaitFrames(10)

        # Exit to entrance area
        self.FollowPath([
            (16, 16),
            (12, 16),
            (12, 99, self.MapDataEnum.FARAWAY_ISLAND.value)
        ])


def ModeRegis(self):
    if (not self.PlayerOnMap(self.MapDataEnum.DESERT_RUINS.value) and
            not self.PlayerOnMap(self.MapDataEnum.ISLAND_CAVE.value) and
            not self.PlayerOnMap(self.MapDataEnum.ANCIENT_TOMB.value)):
        self.logger.info("Please place the player below the target Regi in Desert Ruins, Island Cave or Ancient Tomb, "
                 "then restart the script.")
        os._exit(1)

    while True:
        while not self.OpponentChanged():
            self.ButtonCombo(["Up", "A"])

        self.EncounterPokemon()

        while not self.GetTrainer()["state"] == self.GameState.OVERWORLD:
            continue

        # Exit and re-enter
        self.PressButton("B")
        self.FollowPath([
            (8, 21),
            (8, 11)
        ])


def ModeSouthernIsland(self):
    trainer = self.GetTrainer()
    if (not self.PlayerOnMap(self.MapDataEnum.SOUTHERN_ISLAND_A.value) or
            not 5 <= trainer["posX"] == 13 and trainer["posY"] >= 12):
        self.logger.info("Please place the player below the sphere on Southern Island and restart the script.")
        os._exit(1)

    while True:
        while not self.OpponentChanged():
            self.ButtonCombo(["A", "Up"])

        self.EncounterPokemon()

        # Wait until battle is over
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.WaitFrames(1)
            continue

        # Exit and re-enter
        self.PressButton("B")
        self.FollowPath([
            (13, 99, self.MapDataEnum.SOUTHERN_ISLAND.value),
            (14, -99, self.MapDataEnum.SOUTHERN_ISLAND_A.value)
        ])


def ModeDeoxysPuzzle(self,do_encounter: bool = True):
    def StuckRetryPuzzle(success: bool):
        if not success:
            self.ResetGame()
            return True

    if not self.PlayerOnMap(self.MapDataEnum.BIRTH_ISLAND.value) or self.GetTrainer()["posX"] != 15:
        self.logger.info("Please place the player below the triangle at its starting position on Birth Island, then save before"
                 " restarting the script.")
        os._exit(1)

    delay = 4

    while True:
        while not self.GetTrainer()["state"] == self.GameState.OVERWORLD:
            self.ButtonCombo(["A", 8])

        self.WaitFrames(60)

        # Center
        if self.GetTrainer()["posY"] != 13:
            self.Bonk("Up")
        self.ButtonCombo([delay, "A"])

        # Left
        self.FollowPath([(15, 14), (12, 14)])
        self.ButtonCombo([delay, "Left", "A", delay])

        # Top
        if StuckRetryPuzzle(self.FollowPath([(15, 14), (15, 9)], True, True)): continue
        self.ButtonCombo([delay, "Up", "A", delay])

        # Right
        if StuckRetryPuzzle(self.FollowPath([(15, 14), (18, 14)], True, True)): continue
        self.ButtonCombo([delay, "Right", "A", delay])

        # Middle Left
        if StuckRetryPuzzle(self.FollowPath([(15, 14), (15, 11), (13, 11)], True, True)): continue
        self.ButtonCombo([delay, "Left", "A", delay])

        # Middle Right
        self.FollowPath([(17, 11)])
        self.ButtonCombo([delay, "Right", "A", delay])

        # Bottom
        if StuckRetryPuzzle(self.FollowPath([(15, 11), (15, 13)], True, True)): continue
        self.ButtonCombo([delay, "Down", "A", delay])

        # Bottom Left
        self.FollowPath([(15, 14), (12, 14)])
        self.ButtonCombo([delay, "Left", "A", delay])

        # Bottom Right
        self.FollowPath([(18, 14)])
        self.ButtonCombo([delay, "Right", "A", delay])

        # Bottom
        self.FollowPath([(15, 14)])
        self.ButtonCombo([delay, "Down", delay, "A", delay])

        # Center
        if StuckRetryPuzzle(self.FollowPath([(15, 11)], True, True)): continue

        if not do_encounter:
            self.logger.info("Deoxys puzzle completed. Saving game and starting resets...")
            self.config["bot_mode"] = "deoxys resets"
            self.config["deoxys_puzzle_solved"] = True
            self.SaveGame()
            self.WaitFrames(10)
            return True

        while not self.OpponentChanged():
            self.PressButton("A")
            self.WaitFrames(1)

        self.EncounterPokemon()

        while not self.GetTrainer()["state"] == self.GameState.OVERWORLD:
            continue

        for i in range(0, 4):
            self.PressButton("B")
            self.WaitFrames(15)

        # Exit and re-enter
        self.FollowPath([
            (15, 99, (26, 59)),
            (8, -99, self.apDataEnum.BIRTH_ISLAND.value)
        ])


def ModeDeoxysResets(self):
    if not self.PlayerOnMap(self.MapDataEnum.BIRTH_ISLAND.value) or self.GetTrainer()["posX"] != 15:
        self.logger.info("Please place the player below the triangle at its final position on Birth Island, then save before "
                 "restarting the script.")
        os._exit(1)

    deoxys_frames = self.GetRNGState(self.GetTrainer()["tid"], "deoxys")

    while True:
        # Mash A to reach overworld from intro/title
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.ButtonCombo(["A", 8])

        # Wait for area to load properly
        self.WaitFrames(60)

        if not self.PlayerOnMap(self.MapDataEnum.BIRTH_ISLAND.value) or self.GetTrainer()["posX"] != 15:
            self.logger.info("Please place the player below the triangle at its final position on Birth Island, then save "
                     "before restarting the script.")
            os._exit(1)

        while True:
            emu = self.GetEmu()
            if emu["rngState"] in deoxys_frames:
                self.logger.debug(f"Already rolled on RNG state: {emu['rngState']}, waiting...")
            else:
                while not self.OpponentChanged():
                    self.ButtonCombo(["A", 8])

                deoxys_frames["rngState"].append(emu["rngState"])
                self.WriteFile(f"stats/{self.GetTrainer()['tid']}/deoxys.json",
                          json.dumps(deoxys_frames, indent=4, sort_keys=True))
                self.EncounterPokemon()
            break
        continue


def ModeHoOh(self):
    if not self.PlayerOnMap(self.MapDataEnum.NAVEL_ROCK_I.value) and self.GetTrainer()["posX"] == 12:
        self.logger.info("Please place the player on the steps in front of Ho-oh at Navel Rock and restart the script.")
        os._exit(1)

    while True:
        while not self.OpponentChanged():
            if self.GetTrainer()["posY"] == 9:
                break
            self.ButtonCombo(["Up"])
        else:
            self.EncounterPokemon()

        # Wait until battle is over
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.WaitFrames(1)
            continue

        # Exit and re-enter
        self.PressButton("B")
        self.FollowPath([
            (12, 20),
            (99, 20, self.MapDataEnum.NAVEL_ROCK_H.value),
            (4, 5),
            (99, 5, self.MapDataEnum.NAVEL_ROCK_I.value),
            (12, 20),
            (12, 10)
        ])

def ModeLugia(self):
    trainer = self.GetTrainer()
    if not self.PlayerOnMap(self.MapDataEnum.NAVEL_ROCK_U.value) and trainer["posX"] == 11:
        self.logger.info("Please place the player on the steps in front of Lugia at Navel Rock and restart the script.")
        os._exit(1)

    while True:
        while not self.OpponentChanged():
            if self.GetTrainer()["posY"] < 14:
                break
            self.ButtonCombo(["A", "Up"])
        else:
            self.EncounterPokemon()

        # Wait until battle is over
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.WaitFrames(1)
            continue

        # Exit and re-enter
        self.PressButton("B")
        self.FollowPath([
            (11, 19),
            (99, 19, self.MapDataEnum.NAVEL_ROCK_T.value),
            (4, 5),
            (99, 5, self.MapDataEnum.NAVEL_ROCK_U.value),
            (11, 19),
            (11, 14)
        ])
