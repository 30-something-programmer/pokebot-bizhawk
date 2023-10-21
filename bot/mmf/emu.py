

import fastjsonschema

emu_schema = {
    "type": "object",
    "properties": {
        "frameCount": {"type": "number"},
        "fps": {"type": "number"},
        "detectedGame": {"type": "string"},
        "rngState": {"type": "number"}
    }
}

def LangISO(lang: int):
    match lang:
        case 1:
            return "en"
        case 2:
            return "jp"
        case 3:
            return "fr"
        case 4:
            return "es"
        case 5:
            return "de"
        case 6:
            return "it"


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def GetEmu(self):
    while True:
        try:
            emu = self.LoadJsonMmap(4096, "bizhawk_emu_data-" + self.config["bot_instance_id"])["emu"]
            if self.EmuValidator(emu):
                emu["speed"] = clamp(emu["fps"] / 60, 0.06, 1000)
                emu["language"] = LangISO(emu["language"])
                return emu
        except Exception as e:
            self.logger.debug("Failed to GetEmu(), trying again...")
            self.logger.debug(str(e))
