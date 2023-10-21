import io
import mmap
import cv2
import numpy


def GetScreenshot(self):
    while True:
        screenshot = None
        try:
            screenshot = self.Image.open(io.BytesIO(mmap.mmap(0, 24576, "bizhawk_screenshot-" + self.config["bot_instance_id"])))
            screenshot = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_BGR2RGB)
            return screenshot
        except Exception as e:
            self.logger.debug("Failed to GetScreenshot(), trying again...")
            self.logger.exception(str(e))
            if screenshot is not None:
                screenshot.close()
            # TODO return a black 240x160 image instead of None
            return None