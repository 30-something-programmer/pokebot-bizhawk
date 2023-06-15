# TODO
def mode_farawayMew():
    trainer = GetTrainer()
    if (not player_on_map(MapDataEnum.FARAWAY_ISLAND.value) or not (22 <= trainer["posX"] <= 23 and 8 <= trainer["posY"] <= 10)):
        log.info("Please place the player below the entrance to Mew's area, then restart the script.")
        os._exit(1)
        return

    while True:
        # Enter main area
        while player_on_map(MapDataEnum.FARAWAY_ISLAND.value):
            follow_path([
                (22, 8),
                (22, -99, MapDataEnum.FARAWAY_ISLAND_A.value)
            ])
        
        wait_frames(30)
        hold_button("B")
        
        follow_path([
            (GetTrainer()["posX"], 16),
            (16, 16)
        ])
        # 
        # Follow Mew up while mashing A
        hold_button("Up")

        while not opponent_changed():
            emu_combo(["A", 8])

        identify_pokemon()

        for i in range(0, 6):
            press_button("B")
            wait_frames(10)

        # Exit to entrance area
        follow_path([
            (16, 16),
            (12, 16),
            (12, 99, MapDataEnum.FARAWAY_ISLAND.value)
        ])
