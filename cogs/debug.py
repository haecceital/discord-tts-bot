import discord
from discord.ext import commands
from utils import check_id


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "stats")
    async def stats(self, ctx):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return
        
        await ctx.reply(f"""```{ctx.guild.name}\nlocked: {runtime.locked}\nlistening channel: {runtime.listening_channel}\nrate: {runtime.rate}\nvolume: {runtime.volume}```""")

    @commands.command(name = "echo")
    async def echo(self, ctx, s):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return
        
        await ctx.reply(f"```{s}```")

    @commands.command(name = "check")
    async def check(self, ctx, attrs: str = None):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if runtime.locked and check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        if attrs is None: 
            await ctx.reply(f"```{type(ctx)}\n{str(dir(ctx))[:1900]}```")
            return

        attrs = attrs.split('.')
        target = ctx
        for atr in attrs:
            if hasattr(target, atr):
                target = getattr(target, atr)
            else:
                await ctx.reply(f"no attribute named {atr}")
                return
            
        await ctx.reply(f"```{type(target)}\n{str(dir(target))[:1900]}```")

    @commands.command(name = "lock")
    async def lock(self, ctx):
        if check_id(ctx.author.id):
            await ctx.reply(":x:")
            return

        runtime = self.bot.get_runtime(ctx.guild.id)
        runtime.locked = not runtime.locked

        if runtime.locked:
            await ctx.reply("locked")
        else:
            await ctx.reply("unlocked")

    @commands.command(name = "reload")
    async def reload(self, ctx, cog_name: str):
        if check_id(ctx.author.id):
            await ctx.reply("permission denied")
            return

        cog_name = cog_name.lower()
        
        try:
            self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.reply(f"cogs.{cog_name} successfully reloaded")
        except Exception as e:
            await ctx.reply(f"```py\n{e}\n```")


def setup(bot):
    bot.add_cog(DebugCog(bot))