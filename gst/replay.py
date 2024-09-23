import asyncio
import random

from .pipeline import FILESRC_ELEMENT_NAME, FILEQUEUE_ELEMENT_NAME
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
class ReplayFile(object):
    def __init__(self, pipeline):
        """ Replay a file on EOS """
        self.pipeline = pipeline
        self.filesrc = pipeline.get_by_name(FILESRC_ELEMENT_NAME)

    async def force_replay(self):
        """ Force a replay every 30 seconds """
        while True:
            await asyncio.sleep(random.randrange(0, 10))
            if self.filesrc is None:
                return
            self.pipeline.set_state(Gst.State.PAUSED)
            self.pipeline.seek(1.0, Gst.Format.TIME, 
                (Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT),
                Gst.SeekType.SET, 0.0 , Gst.SeekType.NONE, -1)
            self.pipeline.set_state(Gst.State.PLAYING)
