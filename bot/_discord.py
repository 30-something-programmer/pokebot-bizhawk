# A method of class Bot - derived from __init__

def DiscordMessage(self,
                        webhook_url: str = None,
                        content: str = None,
                        image: str = None,
                        embed: bool = False,
                        embed_title: str = None,
                        embed_description: str = None,
                        embed_fields: object = None,
                        embed_thumbnail: str = None,
                        embed_image: str = None,
                        embed_footer: str = None,
                        embed_color: str = "FFFFFF"):
    try:
        if not webhook_url:
            webhook_url = self.config["discord"]["webhook_url"]
        webhook, embed_obj = self.DiscordWebhook(url=webhook_url, content=content), None
        if image:
            with open(image, "rb") as f:
                webhook.add_file(file=f.read(), filename='image.png')
        if embed:
            embed_obj = self.DiscordEmbed(title=embed_title, color=embed_color)
            if embed_description:
                embed_obj.description = embed_description
            if embed_fields:
                for key, value in embed_fields.items():
                    embed_obj.add_embed_field(name=key, value=value, inline=False)
            if embed_thumbnail:
                with open(embed_thumbnail, "rb") as f:
                    webhook.add_file(file=f.read(), filename='thumb.png')
                embed_obj.set_thumbnail(url='attachment://thumb.png')
            if embed_image:
                with open(embed_image, "rb") as f:
                    webhook.add_file(file=f.read(), filename='embed.png')
                embed_obj.set_image(url='attachment://embed.png')
            if embed_footer:
                embed_obj.set_footer(text=embed_footer)
            embed_obj.set_timestamp()
            webhook.add_embed(embed_obj)
        webhook.execute()
    except Exception as e:
        self.logger.exception(str(e))
        pass


def DiscordRichPresence(self):
    try:
        from asyncio import (
            new_event_loop as new_loop,
            set_event_loop as set_loop)
        set_loop(new_loop())
        RPC = self.Presence("1125400717054713866")
        RPC.connect()
        start = self.time.time()
        # TODO look at setting image to last encounter (limit of 300 art assets on Discord developer portal)
        # Hard code to Rayquaza since only Emerald is supported for now
        while True:
            try:
                RPC.update(
                    state="{} | {}".format(
                            self.GetEncounterLog()["encounter_log"][-1]["pokemon_obj"]["metLocationName"],
                            self.GetEmu()["detectedGame"]),
                    details="{:,} ({:,}✨) | {:,}/h".format(
                            self.GetStats()["totals"].get("encounters", 0),
                            self.GetStats()["totals"].get("shiny_encounters", 0),
                            self.GetEncounterRate()),
                    large_image="rayquaza",
                    start=start,
                    party_id="test",
                    buttons = [{"label": "⏬ Download Pokébot", "url": "https://github.com/40Cakes/pokebot-bizhawk"}])
            except:
                pass
            self.time.sleep(15)
    except Exception as e:
        self.logger.exception(str(e))