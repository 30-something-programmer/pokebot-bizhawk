# Added as part of bot.py Bot class.


bag_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "number"},
        "name": {"type": "string"},
        "quantity": {"type": "number"}
    }
}


def GetBag(self):
    while True:
        try:
            bag = self.LoadJsonMmap(8192, "bizhawk_bag_data-" + self.config["bot_instance_id"])["bag"]
            self.logger.info("bag.py -- GetBag() Pulled bag")
            return bag # Validator throws an exception: Data must be object
            # if BagValidator(bag):
            #     return bag
        except Exception as e:
            self.logger.debug("Failed to GetBag(), trying again...")
            self.logger.debug(str(e))
