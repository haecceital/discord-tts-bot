import asyncio
import re
from hashlib import sha256
from typing import Any, Optional

import discord

# from dataclasses import dataclass


whitelist = [
    "21755f38e3eb43caf10c1a51e31d0df5d817aab8d38a11fdcdc4e5258b1b7a29",
    "ed1dcf6987d889d1414f3fc08b1c12d2614bdb630027f58834dde2cef2adf780",
]


# @dataclass
class RuntimeObj:
    def __init__(self, guild: discord.Guild):
        self.guild = guild

        self.locked = False
        self.listening_channel: Optional[int] = None
        self.rate = "+0%"
        self.volume = "+0%"
        self.timeout = 15
        self.voice = "zh-TW-HsiaoChenNeural"

        self.saved_obj: Any = None

        self.tts_queue = asyncio.Queue()

        self._leave_by_command = False


def check_id(id: int) -> bool:
    if sha256(str(id).encode("utf-8")).hexdigest() not in whitelist:
        return True

    return False


def mention_to_name(text: str, guild: discord.Guild) -> str:
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


def format_sec(secs: int) -> str:
    secs = int(secs)

    days, r = divmod(secs, 86400)
    hours, r = divmod(r, 3600)
    mins, secs = divmod(r, 60)

    return f"{days:02d} days {hours:02d} hours {mins:02d} mins {secs:02d} secs"


def codeblock(text: str, lang: str = "") -> str:
    s = f"{lang}\n{text}"[:1900]

    return f"```{s}```"
