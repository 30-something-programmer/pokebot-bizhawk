import random

def ModeBonk(self):
    direction = self.config["bonk_direction"].lower()

    while True:
        self.logger.info(f"Pathing {direction} until bonk...")

        self.AutoStop()
        while not self.OpponentChanged():
            if direction == "horizontal":
                pos1 = self.Bonk("Left")
                pos2 = self.Bonk("Right")
            else:
                pos1 = self.Bonk("Up")
                pos2 = self.Bonk("Down")
            if pos1 == pos2:
                continue

            self.FollowPath([pos1, pos2])

        self.EncounterPokemon()

        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            continue


def ModeBunnyHop(self):
    self.logger.info("Bunny hopping...")
    i = 0
    
    self.AutoStop(self)
    while not self.OpponentChanged():
        if i < 250:
            self.HoldButton("B")
            self.WaitFrames(1)
        else:
            self.ReleaseAllInputs()
            self.WaitFrames(10)
            i = 0
        i += 1
    self.ReleaseAllInputs()
    self.EncounterPokemon()


def ModeFishing(self):
    self.logger.info(f"Fishing...")
    self.ButtonCombo(["Select", 50])  # Cast rod and wait for fishing animation
    # started_fishing = time.time()
    
    self.AutoStop()
    while not self.OpponentChanged():
        if self.DetectTemplate("oh_a_bite.png") or self.DetectTemplate("on_the_hook.png"):
            self.PressButton("A")
            while self.DetectTemplate("oh_a_bite.png"):
                pass  # This keeps you from getting multiple A presses and failing the catch
        if self.DetectTemplate("not_even_a_nibble.png") or self.DetectTemplate("it_got_away.png"): self.ButtonCombo(
            ["B", 10, "Select"])
        if not self.DetectTemplate("text_period.png"): self.ButtonCombo(
            ["Select", 50])  # Re-cast rod if the fishing text prompt is not visible

    self.EncounterPokemon()


def ModeCoords(self):
    coords = self.config["coords"]
    pos1, pos2 = coords["pos1"], coords["pos2"]
    while True:
        AutoStop()
        while not self.OpponentChanged():
            self.FollowPath([(pos1[0], pos1[1]), (pos2[0], pos2[1])], exit_when_stuck=True)
        self.EncounterPokemon()
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            continue


def ModeSpin(self):  # TODO check if players direction changes, if not spam B (Pokenav)
    try:
        trainer = self.GetTrainer()
        home_coords = (trainer["posX"], trainer["posY"])
        self.logger.info(f"Spinning on the spot, home position is {home_coords}")
        while True:
            AutoStop()
            trainer = self.GetTrainer()
            if self.OpponentChanged(): self.EncounterPokemon()
            if home_coords != (trainer["posX"], trainer[
                "posY"]):  # Note: this will likely fail if the trainer accidentally changes map bank/ID
                self.logger.info(f"Trainer has moved off home position, pathing back to {home_coords}...")
                self.FollowPath([
                    (home_coords[0], trainer["posY"]),
                    (trainer["posX"], home_coords[1])
                ], exit_when_stuck=True)
            directions = ["Up", "Right", "Down", "Left"]
            directions.remove(trainer["facing"])
            self.PressButton(random.choice(directions))
            self.WaitFrames(2)
            if self.GetTrainer()["facing"] == trainer["facing"]:
                # Check if the trainer's facing direction actually changed, press B to cancel PokeNav as it prevents
                # all movement
                self.PressButton("B")
    except Exception as e:
        self.logger.exception(str(e))

def ModePetalburgLoop(self):
    try:
        trainer = self.GetTrainer()
        party = self.GetParty()
        self.logger.info(f"Entering Petalburg fight/heal loop")
        talkCycle = 0
        while True:
            trainer = self.GetTrainer()
            posX = trainer["posX"]

            self.AutoStop()
            if self.OpponentChanged(): self.EncounterPokemon()

            party = self.GetParty()
            tapB = False # For getting out of PokeNav and/or pickup imperfections
            if party:
                isHighHealth = party[0]["hp"] > party[0]["maxHP"] * 0.5
                
                hasViableMoves = False
                for i, move in enumerate(party[0]["enrichedMoves"]):
                    # Ignore banned moves and those with 0 PP
                    if self.IsValidMove(move) and party[0]["pp"][i] > 0:
                        hasViableMoves = True
                if not (isHighHealth and hasViableMoves):
                    # Not in a state to battle, gotta go back to heal
                    if posX < 7 or posX > 20:
                        # Outside and to the right of the Pokemon Center
                        self.HoldButton("B")
                        self.PressButton("Left")
                    elif posX > 7 and posX < 20:
                        # Somehow overshot Pokemon Center, gotta walk back right a bit
                        self.PressButton("Right")
                        tapB = True
                    else:
                        # Right in front of or inside Pokemon Center. Enter building, walk up to Nurse Joy and mash A through her dialogue to heal
                        self.PressButton("Up")
                        if talkCycle > 2:
                            self.HoldButton("A")
                else:
                    # First pokemon in party (probably) has enough HP and PP to actually battle
                    if posX == 7:
                        # Inside Pokemon Center, try to walk down and mash B through Nurse Joy dialogue if it's open
                        self.PressButton("Down")
                        if talkCycle > 2:
                            self.HoldButton("B")
                    elif posX > 7:
                        # Outside and still in the Rustboro tile, run right
                        self.PressButton("Right")
                        self.HoldButton("B")
                    elif posX < 4 or trainer["facing"] == "Left":
                        # In the same tile as the grass, but not in the grass yet. Or in the grass and facing left, so we want to turn right as simpler a alternative to spinning
                        self.PressButton("Right")
                        tapB = True
                    else:
                        # Must be in the grass and not facing left, so turn left as a simpler alternative to spinning
                        self.PressButton("Left")
                        tapB = True

            self.WaitFrames(2)
            talkCycle = (talkCycle + 1) % 4 # to pace button mashing of text boxes and force A/B button holding to reset
            if talkCycle == 0:
                self.ReleaseAllInputs()

            if tapB:
                self.WaitFrames(1)
                if self.GetTrainer()["facing"] == trainer["facing"]:
                    # Check if the trainer's facing direction actually changed, press B to cancel PokeNav as it prevents
                    # all movement
                    self.PressButton("B")
    except Exception as e:
        self.logger.exception(str(e))#


def ModeSweetScent(self):
    self.logger.info(f"Using Sweet Scent...")
    AutoStop()
    self.StartMenu("pokemon")
    self.PressButton("A")  # Select first pokemon in party
    # Search for sweet scent in menu
    while not self.DetectTemplate("sweet_scent.png"):
        self.PressButton("Down")
    self.ButtonCombo(["A", 300])  # Select sweet scent and wait for animation
    self.EncounterPokemon()


def ModePremierBalls(self):
    while not self.DetectTemplate("mart/times_01.png"):
        self.PressButton("A")
        if self.DetectTemplate("mart/you_dont.png"):
            return False
        self.WaitFrames(30)
    self.PressButton("Right")
    self.WaitFrames(15)
    if not self.DetectTemplate("mart/times_10.png") and not self.DetectTemplate("mart/times_11.png"):
        return False
    if self.DetectTemplate("mart/times_11.png"):
        self.PressButton("Down")
    return True

def AutoStop(self):
    if self.config["auto_stop"]: 
        bag = self.GetBag()
        for item in bag["Poké Balls"]:
            if item["quantity"] > 0:
                return
    else:
        return

    self.logger.info(f"Ran out of Balls, pausing the bot...")
    input("Press Enter to continue...")