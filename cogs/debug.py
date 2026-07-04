from time import time

from discord.ext import commands

from utils import check_id, codeblock, format_sec


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        channel_name = (
            self.bot.get_channel(runtime.listening_channel)
            if runtime.listening_channel is not None
            else None
        )

        stat = f"bot uptime: {format_sec(time() - self.bot.start_time)}\n"
        stat += "\n"

        stat += f"server: {runtime.guild.name}\n"
        stat += f"locked: {runtime.locked}\n"
        stat += f"current voice channel: {None if ctx.voice_client is None else ctx.voice_client.channel}\n"
        stat += f"listening channel: {channel_name}\n"
        stat += f"rate: {runtime.rate}\n"
        stat += f"volume: {runtime.volume}\n"
        stat += f"timeout: {runtime.timeout}"

        stat = codeblock(stat)

        await ctx.reply(stat)

    @commands.command(name="echo")
    async def echo(self, ctx, *, s: str):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        await ctx.reply(codeblock(s))

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        runtime = await self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        await ctx.reply(format_sec(time() - self.bot.start_time))

    @commands.command(name="lock")
    async def lock(self, ctx):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        runtime = await self.bot.get_runtime(ctx.guild.id)
        runtime.locked = not runtime.locked

        if runtime.locked:
            await ctx.reply("locked")
        else:
            await ctx.reply("unlocked")

    @commands.command(name="reload")
    async def reload(self, ctx, cog_name: str = None):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        if cog_name is None:
            result = ""
            for cog in self.bot.extensions:
                result += cog.split(".")[-1] + "\n"
            result = codeblock(result)

            await ctx.reply(result)
            return

        cog_name = cog_name.lower()

        try:
            self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.reply(f"cogs.{cog_name} successfully reloaded")
        except Exception as e:
            await ctx.reply(codeblock(e, "py"))

    @commands.command(name="mod")
    async def mod(self, ctx, target: str = None, value=None):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        if target is None:
            result = "timeout"

            await ctx.reply(codeblock(result))
            return

        runtime = await self.bot.get_runtime(ctx.guild.id)
        if target == "timeout":
            if value.isdigit():
                runtime.timeout = int(value)

                await ctx.reply(f"timeout value is set to {value}")
            else:
                await ctx.reply("syntax error")

    @commands.command(name="query")
    async def query(self, ctx, target: str = None):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        if target is None:
            result = "queue"

            await ctx.reply(codeblock(result))
            return

        runtime = await self.bot.get_runtime(ctx.guild.id)
        if target == "queue":
            tts_queue = runtime.tts_queue

            result = "queue size: " + str(tts_queue.qsize()) + "\n\n"
            for i in range(tts_queue.qsize()):
                tmp = tts_queue._queue[i]
                tmp = tmp.get("content")
                result += (
                    tmp if len(tmp) <= 20 else tmp[:20] + f"... {len(tmp) - 20}"
                ) + "\n"

            await ctx.reply(codeblock(result))


def setup(bot):
    bot.add_cog(DebugCog(bot))
