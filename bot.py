import asyncio
import os
from time import time

import discord
from discord.ext import commands

from utils import RuntimeObj


class TTSBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.runtime = {}
        self.get_file = {}
        self.start_time = time()

    async def on_ready(self):
        print(f">>{self.user} is online<<")

    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            cog_path = f"cogs.{filename[:-3]}"
            try:
                self.load_extension(cog_path)
            except Exception as e:
                print(f"load falied {cog_path}\n{e}")

    async def voice_init(self, runtime: RuntimeObj):
        tts_queue = runtime.tts_queue
        start_time = time()
        try:
            while True:
                item = await tts_queue.get()

                voice_client = runtime.guild.voice_client
                if voice_client:
                    res = await self.get_file[item["proc"]](item["content"], runtime)
                    if res is None:
                        continue

                    source, after_playing = res
                    voice_client.play(source, after=after_playing)

                    start_time = time()

                    while voice_client.is_playing():
                        if tts_queue.qsize() >= 1:
                            if time() - start_time > runtime.timeout:
                                voice_client.stop()

                        await asyncio.sleep(0.25)

                tts_queue.task_done()

        except asyncio.CancelledError:
            pass

    async def get_runtime(self, guild_id: int):
        if guild_id not in self.runtime:
            self.runtime[guild_id] = RuntimeObj(
                self.get_guild(guild_id) or (await self.fetch_guild(guild_id))
            )

            asyncio.create_task(self.voice_init(self.runtime[guild_id]))

        return self.runtime[guild_id]


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

tts_bot = TTSBot(command_prefix="!", intents=intents, help_command=None)

tts_bot.load_cogs()
