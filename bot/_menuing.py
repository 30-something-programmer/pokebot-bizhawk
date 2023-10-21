import os

def StartMenu(self, entry: str):
    """
    Function to open any start menu item - presses START, finds the menu entry and opens it
    :param entry: String of menu option to select
    :return: Boolean value of whether menu item was selected
    """
    if entry not in ["bag", "bot", "exit", "option", "pokedex", "pokemon", "pokenav", "save"]:
        return False

    self.logger.info(f"Opening start menu entry: {entry}")
    filename = f"start_menu/{entry.lower()}.png"

    self.ReleaseAllInputs()

    while not  self.DirectTemplate("start_menu/select.png"):
        self.ButtonCombo(["B", "Start"])

        for _ in range(10):
            if self.DirectTemplate("start_menu/select.png"):
                break
            self.WaitFrames(1)

    self.WaitFrames(5)

    while not self.DirectTemplate(filename):  # Find menu entry
        self.ButtonCombo(["Down", 10])

    while self.DirectTemplate(filename):  # Press menu entry
        self.ButtonCombo(["A", 10])
    return True


def BagMenu(self, category: str, item: str):
    """
    Function to find an item in the bag and use item in battle such as a pokeball
    :param category: String value of bag section selection
    :param item: String value of item
    :return: Boolean value of whether item was found
    """
    if category not in ["berries", "items", "key_items", "pokeballs", "tms&hms"]:
        return False

    self.logger.info(f"Scrolling to bag category: {category}...")

    while not self.DirectTemplate(f"start_menu/bag/{category.lower()}.png"):
        self.ButtonCombo(["Right", 25])  # Press right until the correct category is selected

    self.WaitFrames(60)  # Wait for animations

    self.logger.info(f"Scanning for item: {item}...")

    i = 0
    while not  self.DirectTemplate(f"start_menu/bag/items/{item}.png") and i < 50:
        if i < 25:
            self.ButtonCombo(["Down", 15])
        else:
            self.ButtonCombo(["Up", 15])
        i += 1

    if  self.DirectTemplate(f"start_menu/bag/items/{item}.png"):
        self.logger.info(f"Using item: {item}...")
        while self.GetTrainer()["state"] == self.GameState.BAG_MENU:
            self.ButtonCombo(["A", 30])  # Press A to use the item
        return True
    return False


def PickupItems(self):
    """
    If using a team of Pokémon with the ability "pickup", this function will take the items from the pokemon in
    your party if 3 or more Pokémon have an item
    """
    if self.GetTrainer()["state"] != self.GameState.OVERWORLD:
        return

    item_count = 0
    pickup_mon_count = 0

    for i, pokemon in enumerate(self.GetParty()):
        held_item = pokemon['heldItem']

        if pokemon["name"] in self.pickup_pokemon and held_item != 0:
            item_count += 1

            pickup_mon_count += 1
            self.logger.info(f"Pokemon {i}: {pokemon['name']} has item: {self.item_list[held_item]}")

    if item_count < self.config["pickup_threshold"]:
        self.logger.info(f"Party has {item_count} item(s), won't collect until at threshold {self.self.config['pickup_threshold']}")
        return

    self.WaitFrames(60)  # Wait for animations
    StartMenu("pokemon")  # Open Pokémon menu
    self.WaitFrames(65)

    for pokemon in self.GetParty():
        if pokemon["name"] in self.pickup_pokemon and pokemon["heldItem"] != 0:
            # Take the item from the Pokémon
            self.ButtonCombo(["A", 15, "Up", 15, "Up", 15, "A", 15, "Down", 15, "A", 75, "B"])
            item_count -= 1

        if item_count == 0:
            break

        self.ButtonCombo([15, "Down", 15])

    # Close out of menus
    for _ in range(5):
        self.PressButton("B")
        self.WaitFrames(20)


def SaveGame(self):
    """Function to save the game via the save option in the start menu"""
    try:
        self.logger.info("Saving the game...")

        i = 0
        StartMenu("save")
        while i < 2:
            while not  self.DirectTemplate("start_menu/save/yes.png"):
                self.WaitFrames(10)
            while  self.DirectTemplate("start_menu/save/yes.png"):
                self.ButtonCombo(["A", 30])
                i += 1
        self.WaitFrames(500)  # Wait for game to save
        self.PressButton("SaveRAM")  # Flush Bizhawk SaveRAM to disk
    except Exception as e:
        self.logger.exception(str(e))


def ResetGame(self):
    self.logger.info("Resetting...")
    self.HoldButton("Power")
    self.WaitFrames(10)
    self.ReleaseButton("Power")
    self.WaitFrames(60)


def CatchPokemon(self):
    """
    Function to catch pokemon
    :return: Boolean value of whether Pokémon was successfully captured
    """
    opponent = self.GetOpponent()
    try:
        while not  self.DirectTemplate("battle/fight.png"):
            self.ReleaseAllInputs()
            self.ButtonCombo(["B", "Up", "Left"])  # Press B + up + left until FIGHT menu is visible

        if not self.self.config["auto_catch"]:
            input(
                "Pausing bot for manual catch (pause pokebot.lua script so you can control your character). "
                "Press Enter to continue once pokebot.lua is running again...")
            return True
        else:
            self.logger.info("Attempting to catch Pokemon...")


        if self.self.config["use_spore"]:  # Use Spore to put opponent to sleep to make catches much easier
            self.logger.info("Attempting to sleep the opponent...")
            i, spore_pp, spore_move_num = 0, 0, -1

            ability = opponent["ability"][opponent["altAbility"]]
            can_spore = ability not in self.no_sleep_abilities

            if (opponent["status"] == 0) and can_spore:
                for move in self.GetParty()[0]["enrichedMoves"]:
                    if move["name"] == "Spore":
                        spore_pp = move["pp"]
                        spore_move_num = i
                    i += 1

                if spore_pp != 0:
                    self.ButtonCombo(["A", 15])
                    seq = []
                    if spore_move_num == 0:
                        seq = ["Up", "Left"]
                    elif spore_move_num == 1:
                        seq = ["Up", "Right"]
                    elif spore_move_num == 2:
                        seq = ["Left", "Down"]
                    elif spore_move_num == 3:
                        seq = ["Right", "Down"]

                    while not self.DirectTemplate("spore.png"):
                        self.ButtonCombo(seq)

                    self.ButtonCombo(["A", 240])  # Select move and wait for animations
            elif not can_spore:
                self.logger.info(f"Can't sleep the opponent! Ability is {ability}")

        while not self.DirectTemplate("battle/bag.png"):
            self.ReleaseAllInputs()
            self.ButtonCombo(["B", "Up", "Right"])  # Press B + up + right until BAG menu is visible

        while True:
            if self.DirectTemplate("battle/bag.png"):
                self.PressButton("A")

            # Preferred ball order to catch wild mons + exceptions 
            # TODO read this data from memory instead
            if self.GetTrainer()["state"] == self.GameState.BAG_MENU:
                can_catch = False

                # Check if current species has a preferred ball
                if opponent["name"] in self.config["pokeball_override"]:
                    species_rule = self.config["pokeball_override"][opponent["name"]]

                    for ball in species_rule:
                        if BagMenu(category="pokeballs", item=ball):
                            can_catch = True
                            break

                # Check global pokeball priority 
                if not can_catch:
                    for ball in self.config["pokeball_priority"]:
                        if BagMenu(category="pokeballs", item=ball):
                            can_catch = True
                            break

                if not can_catch:
                    self.logger.info("No balls to catch the Pokemon found. Killing the script!")
                    os._exit(1)

            if  self.DirectTemplate("gotcha.png"):  # Check for gotcha! text when a pokemon is successfully caught
                self.logger.info("Pokemon caught!")

                while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
                    self.PressButton("B")

                self.WaitFrames(120)  # Wait for animations

                if self.config["save_game_after_catch"]:
                    SaveGame()

                return True

            if self.GetTrainer()["state"] == self.GameState.OVERWORLD:
                return False
    except Exception as e:
        self.logger.exception(str(e))
        return False


def BattleOpponent(self):
    """
    Function to battle wild pokemon.
    This will only battle with the lead pokemon of the party, and will run if it dies or runs out of PP
    :return: Boolean value of whether battle was won
    """
    ally_fainted = False
    foe_fainted = False

    while not ally_fainted and not foe_fainted and self.GetTrainer()["state"] != self.GameState.OVERWORLD:
        self.logger.info("Navigating to the FIGHT button...")

        while not  self.DirectTemplate("battle/fight.png") and self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            self.ButtonCombo(["B", 10, "Up", 10, "Left", 10])  # Press B + up + left until FIGHT menu is visible

        if self.GetTrainer()["state"] == self.GameState.OVERWORLD:
            return True

        best_move = FindEffectiveMove(self.GetParty()[0], self.GetOpponent())

        if best_move["power"] <= 10:
            self.logger.info("Lead Pokemon has no effective moves to battle the foe!")
            FleeBattle()
            return False

        self.PressButton("A")

        self.WaitFrames(5)

        self.logger.info(f"Best move against foe is {best_move['name']} (Effective power is {best_move['power']})")

        match int(best_move["index"]):
            case 0:
                self.ButtonCombo(["Up", "Left"])
            case 1:
                self.ButtonCombo(["Up", "Right"])
            case 2:
                self.ButtonCombo(["Down", "Left"])
            case 3:
                self.ButtonCombo(["Down", "Right"])

        self.PressButton("A")

        self.WaitFrames(5)

        while self.GetTrainer()["state"] != self.GameState.OVERWORLD and not  self.DirectTemplate("battle/fight.png"):
            self.PressButton("B")
            self.WaitFrames(1)

        ally_fainted = self.GetParty()[0]["hp"] == 0
        foe_fainted = self.GetOpponent()["hp"] == 0

    if ally_fainted:
        self.logger.info("Lead Pokemon fainted!")
        FleeBattle()
        return False
    elif foe_fainted:
        self.logger.info("Battle won!")
    return True


def IsValidMove(self, move: dict):
    return move["name"] not in self.config["banned_moves"] and move["power"] > 0


def FindEffectiveMove(self, ally: dict, foe: dict):
    move_power = []

    for i, move in enumerate(ally["enrichedMoves"]):
        power = move["power"]

        # Ignore banned moves and those with 0 PP
        if not IsValidMove(move) or ally["pp"][i] == 0:
            move_power.append(0)
            continue

        # Calculate effectiveness against opponent's type(s)
        matchups = self.type_list[move["type"]]

        for foe_type in foe["type"]:
            if foe_type in matchups["immunes"]:
                power *= 0
            elif foe_type in matchups["weaknesses"]:
                power *= 0.5
            elif foe_type in matchups["strengths"]:
                power *= 2

        # STAB
        for ally_type in ally["type"]:
            if ally_type == move["type"]:
                power *= 1.5

        move_power.append(power)

    # Return info on the best move
    move_idx = move_power.index(max(move_power))
    return {
        "name": ally["enrichedMoves"][move_idx]["name"],
        "index": move_idx,
        "power": max(move_power)
    }


def FleeBattle(self):
    """Function to run from wild pokemon"""
    try:
        self.logger.info("Running from battle...")
        while self.GetTrainer()["state"] != self.GameState.OVERWORLD:
            while not  self.DirectTemplate("battle/run.png") and self.GetTrainer()["state"] != self.GameState.OVERWORLD:
                self.ButtonCombo(["Right", 5, "Down", "B", 5])
            while  self.DirectTemplate("battle/run.png") and self.GetTrainer()["state"] != self.GameState.OVERWORLD:
                self.PressButton("A")
            self.PressButton("B")
        self.WaitFrames(30)  # Wait for battle fade animation
    except Exception as e:
        self.logger.exception(str(e))
