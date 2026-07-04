import discord, os, time, asyncio
from discord.ext import commands
from utils import RuntimeObj, voice_init


class TTSBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.runtime = {}
        self.start_time = time.time()

    async def on_ready(self):
        print(f">>{bot.user} is online<<")

    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            if not filename.endswith(".py") or filename.startswith("_"): continue

            cog_path = f"cogs.{filename[:-3]}"
            try:
                self.load_extension(cog_path)
            except Exception as e:
                print(f"load falied {cog_path}\n{e}")

    async def get_runtime(self, guild_id: int):
        if guild_id not in self.runtime:
            self.runtime[guild_id] = RuntimeObj(self.get_guild(guild_id) or (await self.fetch_guild(guild_id)))
            
            asyncio.create_task(voice_init(self.runtime[guild_id]))

        return self.runtime[guild_id]



intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = TTSBot(
    command_prefix = '!',
    intents = intents,
    # help_command = None
)

bot.load_cogs()