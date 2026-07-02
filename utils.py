import hashlib
from dataclasses import dataclass
from typing import Optional


whitelist = [
"21755f38e3eb43caf10c1a51e31d0df5d817aab8d38a11fdcdc4e5258b1b7a29"
]


def sha256(s: str | int) -> str:
    return 

def check_id(id: int):
    if hashlib.sha256(str(id).encode("utf-8")).hexdigest() not in whitelist:
        return True

    return False

@dataclass
class RuntimeObj:
    id: int
    
    locked: bool = False
    listening_channel: Optional[int] = None
    rate: str = "+0%"
    volume: str = "+0%"