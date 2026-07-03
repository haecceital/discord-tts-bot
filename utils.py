import hashlib, discord, os, edge_tts, re
from dataclasses import dataclass
from typing import Optional


whitelist = [
"21755f38e3eb43caf10c1a51e31d0df5d817aab8d38a11fdcdc4e5258b1b7a29",
"ed1dcf6987d889d1414f3fc08b1c12d2614bdb630027f58834dde2cef2adf780"
]

ffmpeg_path = "./ffmpeg" if os.getenv("RENDER") else "ffmpeg"


def check_id(id: int) -> bool:
    if hashlib.sha256(str(id).encode("utf-8")).hexdigest() not in whitelist:
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
        output_filename = "tts_output.mp3"
        
        VOICE = "zh-TW-HsiaoChenNeural"
        communicate = edge_tts.Communicate(
            text,
            VOICE,
            rate = rate,
            volume = volume
        )
        await communicate.save(output_filename)

        def after_playing(error):

            if os.path.exists(output_filename):
                os.remove(output_filename)

    source = discord.FFmpegPCMAudio(executable = ffmpeg_path, source = output_filename)

    voice_client.play(source, after = after_playing)

def format_sec(secs: int) -> str:
    secs = int(secs)

    days, r = divmod(secs, 86400)    
    hours, r = divmod(r, 3600)    
    mins, secs = divmod(r, 60)

    return f"{days:02d}:{hours:02d}:{mins:02d}:{secs:02d}"


@dataclass
class RuntimeObj:
    id: int
    
    locked: bool = False
    listening_channel: Optional[int] = None
    rate: str = "+0%"
    volume: str = "+0%"