import fastjsonschema

block_schema = {
            "type": "object",
            "properties": {
                "block_list" : {"type": "array"}
            }
        }


def GetBlockList(self):
    CatchBlockListYml = self.ReadFile(self.catchBlockListYmlFile)
    if CatchBlockListYml:
        CatchBlockList = self.yaml.load(CatchBlockListYml)
        try:
            if self.BlockListValidator(CatchBlockList):
                return CatchBlockList
            return None
        except fastjsonschema.exceptions.JsonSchemaDefinitionException as e:
            self.logger.error(str(e))
            self.logger.error("Block list is invalid!")
            return None

def BlockListManagement(self, pkmName, catch):
    # read current block list into array
    blockList = GetBlockList()
    if catch:
        for i,x in enumerate(blockList["block_list"]):
            if pkmName == x:
                # remove the selected mon from the array
                blockList["block_list"].pop(i)
        # write back to yml
        data = self.yaml.load(self.ReadFile(self.catchBlockListYmlFile))
        data["block_list"] = blockList["block_list"]
        with open(self.catchBlockListYmlFile, "w") as fp:
            self.yaml.dump(data, fp)
    if not catch:
        # add pokemon to the block list
        blockList["block_list"].append(pkmName)
        
        # write back to yml
        data = self.yaml.load(self.ReadFile(self.catchBlockListYmlFile))
        data["block_list"] = blockList["block_list"]
        with open(self.catchBlockListYmlFile, "w") as fp:
            self.yaml.dump(data, fp)


    #add/remove as necessary depending on catch bool
    #write back to file
    
