import discord, os, edge_tts, asyncio, hashlib
from discord.ext import commands


MY_ID = "21755f38e3eb43caf10c1a51e31d0df5d817aab8d38a11fdcdc4e5258b1b7a29"
locked = False
listening_channel = None

speak_rate = "+0%"
speak_volume = "+0%"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "!", intents = intents)


def sha256(s: str | int) -> str:
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()

def check_id(id: int):
    if not locked: return False

    if sha256(id) != MY_ID: return True

    return False

async def play_voice(voice_client, text: str):
    if voice_client.is_playing():
        voice_client.stop()


    output_filename = "tts_output.mp3"
    
    VOICE = "zh-TW-HsiaoChenNeural"
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate = speak_rate,
        volume = speak_volume
    )
    await communicate.save(output_filename)

    source = discord.FFmpegPCMAudio(executable = "ffmpeg", source = output_filename)
    
    def after_playing(error):

        if os.path.exists(output_filename):
            os.remove(output_filename)

    voice_client.play(source, after = after_playing)

cmds = [
"!join",
"!leave",
"!tts",
"!lock",
"!listen",
"!check",
"!volume",
"!rate"
]

@bot.event
async def on_ready():
    print(f">>{bot.user} is onlin<<")

@bot.command()
async def join(ctx):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.reply(f"joined {channel.name}")
    else:
        await ctx.reply("join a voice channel first")

@bot.command()
async def leave(ctx):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.reply("goodbye")
    else:
        await ctx.reply("currently not in voice channel")

@bot.command()
async def check(ctx, atrs: str = None):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    if atrs is None: 
        await ctx.reply(f"```{type(ctx)}\n{str(dir(ctx))[:1900]}```")
        return

    atrs = atrs.split('.')
    target = ctx
    for atr in atrs:
        if hasattr(target, atr):
            target = getattr(target, atr)
        else:
            await ctx.reply(f"no attribute named {atr}")
            return
        
    await ctx.reply(f"```{type(target)}\n{str(dir(target))[:1900]}```")

@bot.command()
async def lock(ctx):
    if sha256(ctx.author.id) != MY_ID:
        await ctx.reply("我不要啊")
        return

    global locked
    locked = not locked

    if locked:
        await ctx.reply("locked")
    else:
        await ctx.reply("unlocked")

@bot.command()
async def rate(ctx, tmp_rate: str = None):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    global speak_rate
    if tmp_rate is not None and (not (tmp_rate.startswith("+") or tmp_rate.startswith("-")) or not tmp_rate.endswith("%")):
        await ctx.reply("syntax error")
        return

    if tmp_rate is None: speak_rate = "+0%"
    else: speak_rate = tmp_rate
    await ctx.reply(f"rate is set to {speak_rate}")

@bot.command()
async def volume(ctx, tmp_volume: str = None):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    global speak_volume
    if tmp_volume is not None and (not (tmp_volume.startswith("+") or tmp_volume.startswith("-")) or not tmp_volume.endswith("%")):
        await ctx.reply("syntax error")
        return

    if tmp_volume is None: speak_volume = "+0%"
    else: speak_volume = tmp_volume
    await ctx.reply(f"volume is set to {speak_volume}")

@bot.command()
async def listen(ctx):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    global listening_channel
    if listening_channel != ctx.channel.id:
        listening_channel = ctx.channel.id

        await ctx.reply(f"start listening {ctx.channel.name}")
    else:
        listening_channel = None

        await ctx.reply(f"stop listening {ctx.channel.name}")

@bot.event
async def on_message(message: discord.Message):
    try:
        if message.author == bot.user: return
        if listening_channel != message.channel.id: return
        if check_id(message.author.id): return        
        for cmd in cmds:
            if message.content.startswith(cmd): return

        voice_client = message.guild.voice_client
        if not voice_client:
            if ctx.author.voice:
                voice_client = await ctx.author.voice.channel.connect()
            else:
                await ctx.reply("join a voice channel before using tts")
                return


        await play_voice(voice_client, message.content)
    finally:
        await bot.process_commands(message)

@bot.command()
async def tts(ctx, *, text: str):
    if check_id(ctx.author.id):
        await ctx.reply("我不要啊")
        return

    voice_client = ctx.voice_client
    if not voice_client:
        if ctx.author.voice:
            voice_client = await ctx.author.voice.channel.connect()
        else:
            await ctx.reply("join a voice channel before using tts")
            return


    await play_voice(voice_client, text)
