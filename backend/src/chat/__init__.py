"""與大師對談服務"""

from .master import generate_master_reply, stream_master_reply
from .fortune import stream_fortune_reply

__all__ = ["generate_master_reply", "stream_master_reply", "stream_fortune_reply"]
