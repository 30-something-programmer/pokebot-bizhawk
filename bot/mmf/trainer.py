trainer_schema = {
    "type": "object",
    "properties": {
        "tid": {"type": "number"},
        "sid": {"type": "number"},
        "state": {"type": "number"},
        "mapId": {"type": "number"},
        "mapBank": {"type": "number"},
        "posX": {"type": "number"},
        "posY": {"type": "number"},
        "facing": {"type": "string"},
        "roamerMapId": {"type": "number"}
    }
}

def GetTrainer(self):
    # Run in a loop as we won't always receive good data from the compile
    while True:
        try:
            
            trainer = self.LoadJsonMmap(4096, "bizhawk_trainer_data-" + self.config["bot_instance_id"])["trainer"]
            self.logger.info("Loading trainer info - " + self.config["bot_instance_id"])
            
            if self.TrainerValidator(trainer):
                return trainer
        except Exception as e:
            self.logger.info("Failed to GetTrainer(), trying again...")
            self.logger.info(str(e))
