# A method of class Bot - derived from __init__
# This method stops the bot from functioning

def Stop(self):
    if self.isRunning:
        self.logger.info(self.name + " stopped")
        self.isRunning = False
    else:
        self.logger.info(self.name + " is not running")