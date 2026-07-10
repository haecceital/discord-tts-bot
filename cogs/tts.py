import asyncio
import os
from uuid import uuid4

import discord
import edge_tts
from discord.ext import commands

from utils import RuntimeObj, check_id, mention_to_name

ffmpeg_path = "./ffmpeg" if os.getenv("RENDER") else "ffmpeg"


def check_format(text: str) -> bool:
    if len(text) < 3:
        return False
    elif text[0] != "-" and text[0] != "+":
        return False
    elif text[-1] != "%":
        return False
    elif not text[1:-1].isdigit():
        return False

    return True


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.get_file["tts"] = self.get_file

    async def get_file(self, content: str, runtime: RuntimeObj):
        output = f"tts_{uuid4().hex}.mp3"

        communicate = edge_tts.Communicate(
            content, runtime.voice, rate=runtime.rate, volume=runtime.volume
        )
        try:
            await communicate.save(output)
        except edge_tts.exceptions.NoAudioReceived:
            return

        def after_playing(error):
            if os.path.exists(output):
                os.remove(output)

        source = discord.FFmpegPCMAudio(executable=ffmpeg_path, source=output)

        return source, after_playing

    @commands.command(name="join")
    async def join(self, ctx):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        if ctx.author.voice or isinstance(ctx.channel, discord.VoiceChannel):
            channel = None
            if ctx.author.voice:
                channel = ctx.channel
            else:
                channel = ctx.channel

            if ctx.voice_client:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()

            await ctx.reply(f"joined {channel.name}")
        else:
            await ctx.reply("join a voice channel first")

    @commands.command(name="leave")
    async def leave(self, ctx):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.reply("goodbye")

            runtime._leave_by_command = True

            if runtime.listening_channel:
                await ctx.reply(
                    f"stop listening {self.bot.get_channel(runtime.listening_channel)}"
                )
                runtime.listening_channel = None
        else:
            await ctx.reply("currently not in voice channel")

    @commands.command(name="listen")
    async def listen(self, ctx):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        if not ctx.voice_client:
            await ctx.reply("im not in a voice channel")
            return

        if runtime.listening_channel != ctx.channel.id:
            runtime.listening_channel = ctx.channel.id

            await ctx.reply(f"start listening {ctx.channel.name}")
        else:
            runtime.listening_channel = None

            await ctx.reply(f"stop listening {ctx.channel.name}")

    @commands.command(name="rate")
    async def rate(self, ctx, rate: str = ""):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        if rate == "":
            runtime.rate = "+0%"
        elif check_format(rate):
            runtime.rate = rate
        else:
            await ctx.reply("syntax error")
            return

        await ctx.reply(f"rate is set to {runtime.rate}")

    @commands.command(name="volume")
    async def volume(self, ctx, volume: str = ""):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        if volume == "":
            runtime.volume = "+0%"
        elif check_format(volume):
            runtime.volume = volume
        else:
            await ctx.reply("syntax error")
            return

        await ctx.reply(f"volume is set to {runtime.volume}")

    @commands.command(name="tts")
    async def tts(self, ctx, *, text: str):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.add_reaction("💩")
            await ctx.reply(":x:")
            return

        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.reply("join a voice channel before using tts")
            return

        await ctx.message.add_reaction(":Air:1458671145845788744")

        content = mention_to_name(text, ctx.guild)
        await runtime.tts_queue.put({"proc": "tts", "content": content})

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.author.bot:
            return

        if message.guild is None:
            await message.reply("unexpected error ocurred")
            return

        runtime = await self.bot.get_runtime(message.guild.id)
        if runtime.listening_channel != message.channel.id:
            return
        if runtime.locked and check_id(message.author.id):
            await message.add_reaction("💩")
            return
        if message.content.startswith("!"):
            return

        voice_client = message.guild.voice_client
        if not voice_client:
            await message.reply("im not in a voice channel")

        await message.add_reaction(":Air:1458671145845788744")

        content = mention_to_name(message.content, message.guild)
        await runtime.tts_queue.put({"proc": "tts", "content": content})

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        if before.channel is not None and after.channel is None:
            await asyncio.sleep(1.5)

            runtime = await self.bot.get_runtime(member.guild.id)

            if not runtime._leave_by_command:
                await asyncio.sleep(1.5)

                await before.channel.connect()
                return

            runtime._leave_by_command = False
            runtime = await self.bot.get_runtime(member.guild.id)

            try:
                while not runtime.tts_queue.empty():
                    runtime.tts_queue.get_nowait()
            except Exception as e:
                pass


def setup(bot):
    bot.add_cog(TTSCog(bot))
