import discord, edge_tts, os, re
from discord.ext import commands
from utils import check_id


sound_effects = {
    "what the dog doing": "soundeffects/WhatTheDogDoing.mp3",
    "why are you gay": "soundeffects/WhyAreYouGay.mp3",
    "陽光彩虹小白馬": "soundeffects/SunshineRainbowWhitePony.mp3",
    # "顆秒": "soundeffects/OneTap.mp3",
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

def replace(text: str, guild: discord.Guild) -> str:
    pattern = r"<@[!&]?(\d+)>"

    def match_handler(match):
        user_id = int(match.group(1))
        
        if not guild:
            return match.group(0)
            
        member = guild.get_member(user_id)
        
        if member:
            return f"{member.display_name}"
        else:
            return f"未知用戶"

    return re.sub(pattern, match_handler, text)

async def play_voice(voice_client: discord.VoiceProtocol, text: str, rate: str, volume: str):
    if voice_client.is_playing():
        voice_client.stop()

    output_filename = "tts_output.mp3"
    
    VOICE = "zh-TW-HsiaoChenNeural"
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate = rate,
        volume = volume
    )
    await communicate.save(output_filename)

    try:
        source = discord.FFmpegPCMAudio(executable = "ffmpeg", source = output_filename)
    except:
        source = discord.FFmpegPCMAudio(executable = "./ffmpeg", source = output_filename)
    
    def after_playing(error):

        if os.path.exists(output_filename):
            os.remove(output_filename)

    voice_client.play(source, after = after_playing)


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
    async def play(self, ctx, *, effect_name: str = None):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if effect_name is None:
            result = "```\navaliable effect list:\n"
            for key in sound_effects:
                result += "  " + key + '\n'
            result += "```"

            await ctx.reply(result)
        elif (effect_path := sound_effects.get(effect_name)) is not None:
            voice_client = ctx.voice_client
            if not voice_client:
                await ctx.reply("join a voice channel before using tts")
                return
            
            try:
                source = discord.FFmpegPCMAudio(executable = "ffmpeg", source = effect_path)
            except:
                source = discord.FFmpegPCMAudio(executable = "./ffmpeg", source = effect_path)

            voice_client.play(source)

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
            replace(text, ctx.guild),
            runtime.rate,
            runtime.volume
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        runtime = self.bot.get_runtime(message.guild.id)

        if message.author == self.bot.user: return
        if runtime.listening_channel != message.channel.id: return
        if runtime.locked and check_id(message.author.id): return        
        for cmd in self.bot.cmds:
            if message.content.startswith(cmd): return

        voice_client = message.guild.voice_client
        if not voice_client:
            await message.reply("im not in a voice channel")


        await play_voice(
            voice_client,
            replace(message.content, message.guild),
            runtime.rate,
            runtime.volume
        )


def setup(bot):
    bot.add_cog(TTSCog(bot))