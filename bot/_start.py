import os,json
from threading import Thread

def Start(self):

    def MainLoop(self):
        """This is the main loop that runs in a thread"""
        # TODO modes should always return True once the trainer is back in the overworld after an encounter, else False -
        # TODO then go into a "recovery" mode after each pass, read updated config that gets POSTed by the UI



        while self.isRunning:
            try:
                if self.GetTrainer() and self.GetEmu():  # Test that emulator information is accessible and valid
                    match self.config["bot_mode"]:
                        case "manual":
                            while not self.OpponentChanged():
                                self.WaitFrames(20)
                            self.EncounterPokemon()
                        case "spin":
                            self.ModeSpin()
                        case "petalburg loop":
                            self.ModePetalburgLoop()
                        case "sweet scent":
                            self.ModeSweetScent()
                        case "bunny hop":
                            self.ModeBunnyHop()
                        case "coords":
                            self.ModeCoords()
                        case "bonk":
                            self.ModeBonk()
                        case "fishing":
                            self.ModeFishing()
                        case "starters":
                            self.ModeStarters()
                        case "rayquaza":
                            self.ModeRayquaza()
                        case "groudon":
                            self.ModeGroudon()
                        case "kyogre":
                            self.ModeKyogre()
                        case "southern island":
                            self.ModeSouthernIsland()
                        case "mew":
                            self.ModeMew()
                        case "regis":
                            self.ModeRegis()
                        case "deoxys runaways":
                            self.ModeDeoxysPuzzle()
                        case "deoxys resets":
                            if self.config["deoxys_puzzle_solved"]:
                                self.ModeDeoxysResets()
                            else:
                                self.ModeDeoxysPuzzle(False)
                        case "lugia":
                            self.ModeLugia()
                        case "ho-oh":
                            self.ModeHoOh()
                        case "fossil":
                            self.ModeFossil()
                        case "castform":
                            self.ModeCastform()
                        case "beldum":
                            self.ModeBeldum()
                        case "johto starters":
                            self.ModeJohtoStarters()
                        case "buy premier balls":
                            self.purchased = self.ModePremierBalls()

                            if not self.purchased:
                                self.logger.info(f"Ran out of money to buy Premier Balls. Script ended.")
                                input("Press enter to continue...")
                        case _:
                            self.logger.exception("Couldn't interpret bot mode: " + self.config["bot_mode"])
                            input("Press enter to continue...")
                else:
                    self.ReleaseAllInputs()
                    self.WaitFrames(5)
            except Exception as e:
                self.logger.exception(str(e))

    try:
        main = Thread(target=MainLoop,args=[self])
        main.start()

        # Discord 
        if self.config["discord"]["rich_presence"]:
            from _discord import DiscordRichPresence
            Thread(target=DiscordRichPresence,args=[self]).start()

        # Http Server
        if self.config["server"]["enable"]:
            from _flaskServer import httpServer
            Thread(target=httpServer(self),args=[self]).start()

        # User Interface
        if self.config["ui"]["enable"]:
            import webview
            def OnWindowClose():
                self.ReleaseAllInputs()
                self.logger.info("Dashboard closed on user input...")
                os._exit(1)

            url = f"http://{self.config['server']['ip']}:{self.config['server']['port']}/dashboard"
            window = webview.create_window("PokeBot", url=url, width=self.config["ui"]["width"], height=self.config["ui"]["height"],
                                        text_select=True, zoomable=True)
            window.events.closed += OnWindowClose
            webview.start()
        else:
            main.join()

    except Exception as e:
        self.logger.exception(str(e))
        os._exit(1)

    # Stop the loop before it starts if the bot is already running
    if self.isRunning:
        self.logger.info(self.name + " is already running!")
        return
    else:
        self.isRunning = True
        self.logger.info(self.name + " starting")

    self.ReleaseAllInputs()
    self.PressButton("SaveRAM")  # Flush Bizhawk SaveRAM to disk

