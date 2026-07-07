import os

import discord
from discord.ext import commands

from utils import RuntimeObj, check_id, codeblock

sound_effects = {
    "what the dog doing": "soundeffects/WhatTheDogDoing.mp3",
    "why are you gay": "soundeffects/WhyAreYouGay.mp3",
    "陽光彩虹小白馬": "soundeffects/SunshineRainbowWhitePony.mp3",
    # "顆秒": "soundeffects/OneTap.mp3",
    "creeper": "soundeffects/CreeperHiss.mp3",
    "windows xp shutdown": "soundeffects/WindowsXpShutdown.mp3",
    "sus": "soundeffects/AmongUsStart.mp3",
}

ffmpeg_path = "./ffmpeg" if os.getenv("RENDER") else "ffmpeg"


class SoundCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.get_file["sound"] = self.get_file

    async def get_file(self, content: str, runtime: RuntimeObj):
        source = discord.FFmpegPCMAudio(executable=ffmpeg_path, source=content)

        def after_playing(error):
            pass

        return source, after_playing

    @commands.command(name="play")
    async def play(self, ctx, *, effect: str | None = None):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        if effect is None:
            result = "available effect list:\n"
            for idx, key in enumerate(sound_effects):
                result += f"  {idx}: " + key + "\n"

            result = codeblock(result)

            await ctx.reply(result)
            return

        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.reply("join a voice channel before using play")
            return

        effect_path = sound_effects.get(effect)
        if effect_path is None and effect.isdigit():
            effect_idx = int(effect)

            effect_path = ""
            for idx, key in enumerate(sound_effects):
                if idx == effect_idx:
                    effect_path = sound_effects.get(key)

        if effect_path is None:
            await ctx.reply("syntax error")
            return

        await ctx.message.add_reaction(":Air:1458671145845788744")
        await runtime.tts_queue.put({"proc": "sound", "content": effect_path})


def setup(bot):
    bot.add_cog(SoundCog(bot))
