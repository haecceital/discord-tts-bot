import discord, os, edge_tts, re, asyncio
from hashlib import sha256
# from dataclasses import dataclass
from typing import Optional, Any
from time import time


whitelist = [
"21755f38e3eb43caf10c1a51e31d0df5d817aab8d38a11fdcdc4e5258b1b7a29",
"ed1dcf6987d889d1414f3fc08b1c12d2614bdb630027f58834dde2cef2adf780"
]

ffmpeg_path = "./ffmpeg" if os.getenv("RENDER") else "ffmpeg"

# @dataclass
class RuntimeObj:
    def __init__(self, guild: discord.Guild):
        self.guild = guild

        self.locked = False
        self.listening_channel: Optional[int] = None
        self.rate = "+0%"
        self.volume = "+0%"
        self.timeout = 15

        self.saved_obg: Any = None

        self.tts_queue = asyncio.Queue()


def check_id(id: int) -> bool:
    if sha256(str(id).encode("utf-8")).hexdigest() not in whitelist:
        return True

    return False

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

async def play_voice(
        voice_client: discord.VoiceProtocol,
        path: str = None,
        text: str = None,
        rate: str = None,
        volume: str = None
    ):
    if voice_client.is_playing():
        voice_client.stop()

    def after_playing(error): pass

    if path is None:
        path = "tts_output.mp3"
        
        VOICE = "zh-TW-HsiaoChenNeural"
        communicate = edge_tts.Communicate(
            text,
            VOICE,
            rate = rate,
            volume = volume
        )
        try:
            await communicate.save(path)
        except edge_tts.exceptions.NoAudioReceived:
            return

        def after_playing(error):
            if os.path.exists(path):
                os.remove(path)

    source = discord.FFmpegPCMAudio(executable = ffmpeg_path, source = path)

    voice_client.play(source, after = after_playing)

async def voice_init(runtime: RuntimeObj):
    tts_queue = runtime.tts_queue
    start_time = time()
    try:
        while True:
            item = await tts_queue.get()
            
            voice_client = runtime.guild.voice_client
            if voice_client:
                await play_voice(
                    voice_client,
                    path = item.get("path"),
                    text = item.get("text"),
                    rate = runtime.rate,
                    volume = runtime.volume
                )
                start_time = time()

                while voice_client.is_playing():
                    if (tts_queue.qsize() >= 1):
                        if time() - start_time > runtime.timeout: voice_client.stop()

                    await asyncio.sleep(0.25)
            
            tts_queue.task_done()
            
    except asyncio.CancelledError:
        pass

def format_sec(secs: int) -> str:
    secs = int(secs)

    days, r = divmod(secs, 86400)    
    hours, r = divmod(r, 3600)    
    mins, secs = divmod(r, 60)

    return f"{days:02d} days {hours:02d} hours {mins:02d} mins {secs:02d} secs"

def codeblock(text: str, lang: str = ""):
    return f"```{lang}\n{text}```"