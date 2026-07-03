import inspect, datetime
from discord.ext import commands
from utils import check_id, format_sec
from time import time


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
        stat += f"bot uptime: {format_sec(time() - self.bot.start_time)}\n"
        stat += '\n'

        stat += f"server: {ctx.guild.name}\n"
        stat += f"locked: {runtime.locked}\n"
        stat += f"current voice channel: {ctx.voice_client.channel}\n"
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
        
        await ctx.reply(format_sec(time() - self.bot.start_time))


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

    @commands.command(name = "dump")
    async def dump(self, ctx, *, s: str = None):
        runtime = self.bot.get_runtime(ctx.guild.id)

        if check_id(ctx.author.id):
            await ctx.reply(":x:")
            return
        
        attributes = None
        name = None
        execute = None
        args = None
        save_obj = False
        if s is not None:
            for block in s.split():
                if block.startswith("att="):
                    attributes = block.replace("att=", "")
                elif block.startswith("name="):
                    name = block.replace("name=", "")
                elif block.startswith("exec="):
                    execute = block.replace("exec=", "")
                elif block.startswith("args="):
                    args = [eval(arg) for arg in block.replace("args=", "").split(',')]
                elif block == "save":
                    save_obj = True
            
            if name is None and attributes is None:
                attributes = s

        target = ctx
        if attributes is not None:
            for att in attributes.split('.'):
                if hasattr(target, att): target = getattr(target, att)
                elif att == "origin": target = self.bot
                elif att == "saved_obj": target = runtime.saved_obg
                else:
                    await ctx.reply(f"attribute {att} doesnt exist")
                    return

        if execute:
            if hasattr(target, execute) and (method := getattr(target, execute)):
                try:
                    if not args: args = []
                    result = None
                    if inspect.iscoroutinefunction(method):
                        result = await method(*args)
                    else:
                        result = method(*args)
                    await ctx.send(f"```\ncmd = '{ctx.message.content}'```\n{execute}({str(args)[1:-1]}) successfully executed!\nthe result of it is {result}")

                    if save_obj:
                        runtime.saved_obg = result
                        await ctx.reply("obj saved!")
                except Exception as e:
                    await ctx.reply(f"```py\n{e}```")
        else:
            if name is None: name = ""

            target_class = "type: " + str(type(target))[8:-2] + '\n\n'
            target_str = "" if "object at 0x" in str(target) else "obj: " + str(target) + '\n\n'
            target_normal_atts = "attributes: " + ", ".join([att for att in dir(target) if not att.startswith('_') and name in att]) + "\n\n"
            double_att = [att for att in dir(target) if att.startswith("__") and name in att]
            # target_protected_atts = "protected attributes: " + ", ".join([att for att in dir(target) if att.startswith('_') and att not in double_att and name in att]) + "\n\n"
            target_protected_atts = ""

            await ctx.reply(f"```\n{target_class}{target_str}{target_normal_atts}{target_protected_atts}"[:1996] + "```")

            if save_obj:
                runtime.saved_obg = target
                await ctx.reply("obj saved!")

def setup(bot):
    bot.add_cog(DebugCog(bot))