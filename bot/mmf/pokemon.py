import re
import numpy
from datetime import datetime



pokemon_schema = {
    "type": "object",
    "properties": {
        "altAbility": {"type": "number"},
        "attack": {"type": "number"},
        "attackEV": {"type": "number"},
        "attackIV": {"type": "number"},
        "defense": {"type": "number"},
        "defenseEV": {"type": "number"},
        "defenseIV": {"type": "number"},
        "eventLegal": {"type": "number"},
        "experience": {"type": "number"},
        "friendship": {"type": "number"},
        "hasSpecies": {"type": "number"},
        "heldItem": {"type": "number"},
        "hp": {"type": "number"},
        "hpEV": {"type": "number"},
        "hpIV": {"type": "number"},
        "isBadEgg": {"type": "number"},
        "isEgg": {"type": "number"},
        "language": {"type": "number"},
        "level": {"type": "number"},
        "magicWord": {"type": "number"},
        "mail": {"type": "number"},
        "markings": {"type": "number"},
        "maxHP": {"type": "number"},
        "metGame": {"type": "number"},
        "metLevel": {"type": "number"},
        "metLocation": {"type": "number"},
        "moves": {"type": "array", "maxItems": 4},
        "name": {"type": "string"},
        "otGender": {"type": "number"},
        "otId": {"type": "number"},
        "personality": {"type": "number"},
        "pokeball": {"type": "number"},
        "pokerus": {"type": "number"},
        "pp": {"type": "array", "maxItems": 4},
        "ppBonuses": {"type": "number"},
        "shiny": {"type": "number"},
        "spAttack": {"type": "number"},
        "spAttackEV": {"type": "number"},
        "spAttackIV": {"type": "number"},
        "spDefense": {"type": "number"},
        "spDefenseEV": {"type": "number"},
        "spDefenseIV": {"type": "number"},
        "species": {"type": "number"},
        "speed": {"type": "number"},
        "speedEV": {"type": "number"},
        "speedIV": {"type": "number"},
        "status": {"type": "number"}
    }
}

natures = [
    "Hardy",
    "Lonely",
    "Brave",
    "Adamant",
    "Naughty",
    "Bold",
    "Docile",
    "Relaxed",
    "Impish",
    "Lax",
    "Timid",
    "Hasty",
    "Serious",
    "Jolly",
    "Naive",
    "Modest",
    "Mild",
    "Quiet",
    "Bashful",
    "Rash",
    "Calm",
    "Gentle",
    "Sassy",
    "Careful",
    "Quirky"
]

hiddenPowers = [
    "Fighting",
    "Flying",
    "Poison",
    "Ground",
    "Rock",
    "Bug",
    "Ghost",
    "Steel",
    "Fire",
    "Water",
    "Grass",
    "Electric",
    "Psychic",
    "Ice",
    "Dragon",
    "Dark"
]


def EnrichMonData(self, pokemon: dict):
    """
    Function to add information to the pokemon data extracted from Bizhawk
    :param pokemon: Pokémon data to enrich
    :return: Enriched Pokémon data or None if failed
    """
    try:
        if re.match("^[A-Za-z0-9-]*$", pokemon["name"]):
            
            trainer = self.GetTrainer()
            
            # Human readable location name
            pokemon["metLocationName"] = self.location_list[pokemon["metLocation"]]

            # Human readable pokemon types
            pokemon["type"] = self.pokemon_list[pokemon["name"]]["type"]
            
            # Human readable abilities
            pokemon["ability"] = self.pokemon_list[pokemon["name"]]["ability"][pokemon["altAbility"]]
            
            # Get pokemon nature
            pokemon["nature"] = self.natures[pokemon["personality"] % 25]
            
            # Get zero pad number - e.g.: #5 becomes #005
            pokemon["zeroPadNumber"] = f"{self.pokemon_list[pokemon['name']]['number']:03}"
            
            # Get held item's name
            pokemon["itemName"] = self.item_list[pokemon["heldItem"]]
            
            # IV sum
            pokemon["IVSum"] = (
                pokemon["hpIV"] +
                pokemon["attackIV"] +
                pokemon["defenseIV"] +
                pokemon["spAttackIV"] +
                pokemon["spDefenseIV"] +
                pokemon["speedIV"]
            )

            # Calculate "shiny value" to determine shininess
            # https://bulbapedia.bulbagarden.net/wiki/Personality_value#Shininess
            pBin = format(pokemon["personality"], "032b")
            pokemon["shinyValue"] = int(bin(int(pBin[:16], 2) ^ int(pBin[16:], 2)
                                        ^ trainer["tid"] ^ trainer["sid"])[2:], 2)
            pokemon["shiny"] = True if pokemon["shinyValue"] < 8 else False

            #pokemon["shinyValue"] = 0  # Testing
            #pokemon["shiny"] = True  # Testing

            # Copy move info out of an array (simplifies CSV logging)
            # TODO look at flattening the array instead of doing this
            pokemon["move_1"] = pokemon["moves"][0]
            pokemon["move_2"] = pokemon["moves"][1]
            pokemon["move_3"] = pokemon["moves"][2]
            pokemon["move_4"] = pokemon["moves"][3]
            pokemon["move_1_pp"] = pokemon["pp"][0]
            pokemon["move_2_pp"] = pokemon["pp"][1]
            pokemon["move_3_pp"] = pokemon["pp"][2]
            pokemon["move_4_pp"] = pokemon["pp"][3]
            pokemon["type_1"] = pokemon["type"][0]
            pokemon["type_2"] = "None"
            if len(pokemon["type"]) == 2:
                pokemon["type_2"] = pokemon["type"][1]

            # Add move data to Pokémon (includes move type, power, PP etc.)
            pokemon["enrichedMoves"] = []
            for move in pokemon["moves"]:
                pokemon["enrichedMoves"].append(self.move_list[move])

            # Pokerus
            # TODO get number of days infectious, see - https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9rus#Technical_information
            if pokemon["pokerus"] != 0:
                if pokemon["pokerus"] % 10:
                    pokemon["pokerusStatus"] = "infected"
                else:
                    pokemon["pokerusStatus"] = "cured"
            else:
                pokemon["pokerusStatus"] = "none"

            # Hidden power type
            pokemon["hiddenPowerType"] = self.hiddenPowers[int(numpy.floor((((pokemon["hpIV"] % 2) +
                                            (2 * (pokemon["attackIV"] % 2)) + 
                                            (4 * (pokemon["defenseIV"] % 2)) + 
                                            (8 * (pokemon["speedIV"] % 2)) + 
                                            (16 * (pokemon["spAttackIV"] % 2)) + 
                                            (32 * (pokemon["spDefenseIV"] % 2))) * 15) / 63))]

            # Log encounter time
            now = datetime.now()
            year = f"{now.year}"
            month = f"{now.month :02}"
            day = f"{now.day :02}"
            hour = f"{now.hour :02}"
            minute = f"{now.minute :02}"
            second = f"{now.second :02}"
            pokemon["date"] = f"{year}-{month}-{day}"
            pokemon["time"] = f"{hour}:{minute}:{second}"

            return pokemon
        else:
            return None
    except Exception as e:
        self.logger.debug(str(e))
        return None


def GetOpponent(self):
    while True:
        try:
            opponent = self.LoadJsonMmap(4096, "bizhawk_opponent_data-" + self.config["profile"])["opponent"]
            if opponent and self.pokemonValidator(opponent):
                enriched = EnrichMonData(opponent)
                if enriched:
                    return enriched
        except Exception as e:
            self.logger.debug("Failed to GetOpponent(), trying again...")
            self.logger.debug(str(e))


def GetParty(self):
    while True:
        try:
            party_list = []
            party = self.LoadJsonMmap(8192, "bizhawk_party_data-" + self.config["profile"])["party"]
            if party:
                for pokemon in party:
                    if self.pokemonValidator(pokemon):
                        enriched = EnrichMonData(self, pokemon)
                        if enriched:
                            party_list.append(enriched)
                            continue
                    else:
                        self.WaitFrames(1)
                        # retry -= 1
                        break
                return party_list
        except Exception as e:
            self.logger.error("Failed to GetParty(), trying again...")
            self.logger.error(str(e))
