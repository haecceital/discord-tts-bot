import time
from discord.ext import commands
from utils import check_id, format_sec


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "stats")
    async def stats(self, ctx):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return
        
        channel_name = self.bot.get_channel(runtime.listening_channel) if runtime.listening_channel is not None else None

        stat = "```\n"
        stat += f"server: {ctx.guild.name}\n"
        stat += f"locked: {runtime.locl}\n"
        stat += f"listening channel: {channel_name}\n"
        stat += f"rate: {runtime.rate}\n"
        stat += f"volume: {runtime.volume}\n"
        stat += "```"

        await ctx.reply(stat)

    @commands.command(name = "echo")
    async def echo(self, ctx, s):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return
        
        await ctx.reply(f"```{s}```")

    @commands.command(name = "uptime")
    async def uptime(self, ctx):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return
        
        await ctx.reply(format_sec(time.time() - self.bot.start_time))


    @commands.command(name = "lock")
    async def lock(self, ctx):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        runtime = self.bot.get_runtime(ctx.guild.id)
        runtime.locked = not runtime.locked

        if runtime.locked:
            await ctx.reply("locked")
        else:
            await ctx.reply("unlocked")

    @commands.command(name = "reload")
    async def reload(self, ctx, cog_name: str = None):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        if cog_name is None:
            result = "```\n"
            for cog in self.bot.extensions:
                result += cog.split('.')[-1] + '\n'
            result += "```"

            await ctx.reply(result)
            return

        cog_name = cog_name.lower()
        
        try:
            self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.reply(f"cogs.{cog_name} successfully reloaded")
        except Exception as e:
            await ctx.reply(f"```py\n{e}\n```")


def setup(bot):
    bot.add_cog(DebugCog(bot))