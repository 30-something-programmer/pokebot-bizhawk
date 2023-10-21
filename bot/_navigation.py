

def Bonk(self, direction: str, run: bool = True):
    """
    Function to run until trainer position stops changing
    :param direction: Direction to move
    :param run: Boolean value of whether to run
    :return: Last known player coordinates or None if in a battle
    """
    self.PressButton("B")  # press and release B in case of a random pokenav call

    self.HoldButton(direction)
    last_x = self.GetTrainer()["posX"]
    last_y = self.GetTrainer()["posY"]

    move_speed = 8 if run else 16

    dir_unchanged = 0
    while dir_unchanged < move_speed:
        if run:
            self.HoldButton("B")
            self.WaitFrames(1)

        trainer = self.GetTrainer()
        if last_x == trainer["posX"] and last_y == trainer["posY"]:
            dir_unchanged += 1
            continue

        last_x = trainer["posX"]
        last_y = trainer["posY"]
        dir_unchanged = 0

        if self.OpponentChanged():
            return None

    self.ReleaseAllInputs()
    self.WaitFrames(1)
    self.PressButton("B")
    self.WaitFrames(1)

    return [last_x, last_y]


def FollowPath(self, coords: list, run: bool = True, exit_when_stuck: bool = False):
    direction = None

    for x, y, *map_data in coords:
        self.logger.info(f"Moving to: {x}, {y}")

        stuck_time = 0

        self.ReleaseAllInputs()
        while True:
            if run:
                self.HoldButton("B")

            if self.OpponentChanged():
                self.EncounterPokemon()
                return

            if self.GetTrainer()["posX"] == x and self.GetTrainer()["posY"] == y:
                self.ReleaseAllInputs()
                break
            elif map_data:
                # On map change
                if self.GetTrainer()["mapBank"] == map_data[0][0] and self.GetTrainer()["mapId"] == map_data[0][1]:
                    self.ReleaseAllInputs()
                    break

            last_pos = [self.GetTrainer()["posX"], self.GetTrainer()["posY"]]
            if self.GetTrainer()["posX"] == last_pos[0] and self.GetTrainer()["posY"] == last_pos[1]:
                stuck_time += 1

                if stuck_time % 60 == 0:
                    self.log.info("Bot hasn't moved for a while. Is it stuck?")
                    self.ReleaseButton("B")
                    self.WaitFrames(1)
                    self.PressButton("B")  # Press B occasionally in case there's a menu/dialogue open
                    self.WaitFrames(1)

                    if exit_when_stuck:
                        self.ReleaseAllInputs()
                        return False
            else:
                stuck_time = 0

            if self.GetTrainer()["posX"] > x:
                direction = "Left"
            elif self.GetTrainer()["posX"] < x:
                direction = "Right"
            elif self.GetTrainer()["posY"] < y:
                direction = "Down"
            elif self.GetTrainer()["posY"] > y:
                direction = "Up"

            self.HoldButton(direction)
            self.WaitFrames(1)

        self.ReleaseAllInputs()
    return True


def PlayerOnMap(self, map_data: tuple):
    trainer = self.GetTrainer()
    on_map = trainer["mapBank"] == map_data[0] and trainer["mapId"] == map_data[1]
    self.logger.debug(
        f"Player was not on target map of {map_data[0]},{map_data[1]}. Map was {trainer['mapBank']}, {trainer['mapId']}")
    return on_map
