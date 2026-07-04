import inspect
from discord.ext import commands
from utils import check_id, codeblock


class DumpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "dump")
    async def dump(self, ctx, *, s: str = None):
        runtime = await self.bot.get_runtime(ctx.guild.id)

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
                if block.startswith("obj="):
                    attributes = block.replace("obj=", "")
                elif block.startswith("name="):
                    name = block.replace("name=", "")
                elif block.startswith("exec="):
                    execute = block.replace("exec=", "")
                elif block.startswith("args="):
                    args = [eval(arg) for arg in block.replace("args=", "").split('|')]
                elif block.startswith("kwargs="):
                    kwargs = {}
                    for kw in block.replace("kwargs=", "").split('|'):
                        k, v = kw.split('=', 1)
                        kwargs[k] = eval(v)
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
                    if not kwargs: kwargs = {}
                    result = None
                    if inspect.iscoroutinefunction(method):
                        result = await method(*args, **kwargs)
                    else:
                        result = method(*args)
                    await ctx.send(f"{codeblock(ctx.message.content)}\n{execute}({str(args)[1:-1]}) successfully executed!\nthe result of it is {result}")

                    if save_obj:
                        runtime.saved_obg = result
                        await ctx.reply("obj saved!")
                except Exception as e:
                    await ctx.reply(codeblock(e, "py"))
        else:
            if name is None: name = ""

            target_class = "type: " + str(type(target))[8:-2] + '\n\n'
            target_str = "" if "object at 0x" in str(target) else "obj: " + str(target) + '\n\n'
            target_normal_atts = "attributes: " + ", ".join([att for att in dir(target) if not att.startswith('_') and name in att]) + "\n\n"
            double_att = [att for att in dir(target) if att.startswith("__") and name in att]
            # target_protected_atts = "protected attributes: " + ", ".join([att for att in dir(target) if att.startswith('_') and att not in double_att and name in att]) + "\n\n"
            target_protected_atts = ""

            result = codeblock(f"{target_class}{target_str}{target_normal_atts}{target_protected_atts}")
            if len(result) > 2000: result = result[:1997] + "```"

            await ctx.reply(result)

            if save_obj:
                runtime.saved_obg = target
                await ctx.reply("obj saved!")


def setup(bot):
    bot.add_cog(DumpCog(bot))