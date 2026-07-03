import discord
from discord.ext import commands
from utils import check_id, play_voice, replace


sound_effects = {
    "what the dog doing": "soundeffects/WhatTheDogDoing.mp3",
    "why are you gay": "soundeffects/WhyAreYouGay.mp3",
    "陽光彩虹小白馬": "soundeffects/SunshineRainbowWhitePony.mp3",
    "顆秒": "soundeffects/OneTap.mp3",
    "creeper": "soundeffects/CreeperHiss.mp3",
    "windows xp shutdown": "soundeffects/WindowsXpShutdown.mp3",
    "sus": "soundeffects/AmongUsStart.mp3",
}

def check_format(text: str) -> bool:
    if len(text) < 3: return False
    elif text[0] != '-' or text[0] != '+': return False
    elif text[-1] != '%': return False
    elif not text[1:len(text) - 1].isdigit(): return False

    return True


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "join")
    async def join(self, ctx):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.reply(f"joined {channel.name}")
        else:
            await ctx.reply("join a voice channel first")

    @commands.command(name = "leave")
    async def leave(self, ctx):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.reply("goodbye")
        else:
            await ctx.reply("currently not in voice channel")

    @commands.command(name = "listen")
    async def listen(self, ctx):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if runtime.listening_channel != ctx.channel.id:
            runtime.listening_channel = ctx.channel.id

            await ctx.reply(f"start listening {ctx.channel.name}")
        else:
            runtime.listening_channel = None

            await ctx.reply(f"stop listening {ctx.channel.name}")

    @commands.command(name = "rate")
    async def rate(self, ctx, rate: str = None):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if rate is None:
            runtime.rate = "+0%"
        elif check_format(rate):
            runtime.rate = rate
        else:
            await ctx.reply("syntax error")
            return

        await ctx.reply(f"rate is set to {runtime.rate}")

    @commands.command(name = "volume")
    async def volume(self, ctx, volume: str = None):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if volume is None:
            runtime.volume = "+0%"
        elif check_format(volume):
            runtime.volume = volume
        else:
            await ctx.reply("syntax error")
            return

        await ctx.reply(f"volume is set to {runtime.volume}")

    @commands.command(name = "play")
    async def play(self, ctx, *, effect: str = None):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if effect is None:
            result = "```\navailable effect list:\n"
            for idx, key in enumerate(sound_effects):
                result += f"  {idx}: " + key + '\n'
            result += "```"

            await ctx.reply(result)
        elif (effect_path := sound_effects.get(effect)) is not None:
            voice_client = ctx.voice_client
            if not voice_client:
                await ctx.reply("join a voice channel before using tts")
                return
            
            await play_voice(
                voice_client,
                path = effect_path
            )
        elif effect.isdigit():
            effect = int(effect)

            effect_path = ""
            for idx, key in enumerate(sound_effects):
                if idx == effect: effect_path = sound_effects.get(key)

            await play_voice(
                voice_client,
                path = effect_path
            )

    @commands.command(name = "tts")
    async def tts(self, ctx, *, text: str):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.reply("join a voice channel before using tts")
            return
        
        await play_voice(
            voice_client,
            text = replace(text, ctx.guild),
            rate = runtime.rate,
            volume = runtime.volume
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        runtime = self.bot.get_runtime(message.guild.id)

        if message.author == self.bot.user: return
        if runtime.listening_channel != message.channel.id: return
        if runtime.locked and check_id(message.author.id): return        
        if message.content[0] == "!": return

        voice_client = message.guild.voice_client
        if not voice_client:
            await message.reply("im not in a voice channel")

        await play_voice(
            voice_client,
            text = replace(message.content, message.guild),
            rate = runtime.rate,
            volume = runtime.volume
        )

def setup(bot):
    bot.add_cog(TTSCog(bot))