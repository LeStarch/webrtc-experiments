import asyncio

from .pipeline import FILESRC_ELEMENT_NAME, FILEQUEUE_ELEMENT_NAME
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
class ReplayFile(object):
    def __init__(self, pipeline):
        """ Replay a file on EOS """
        self.filesrc = pipeline.get_by_name(FILESRC_ELEMENT_NAME)
        self.filequeue = pipeline.get_by_name(FILEQUEUE_ELEMENT_NAME)

    async def force_replay(self):
        """ Force a replay every 30 seconds """
        while True:
            await asyncio.sleep(5)
            if self.filesrc is None:
                return
#            self.filesrc.seek_simple(Gst.Format.TIME, 0, 0)
