from .pipeline import FILESRC_ELEMENT_NAME, FILEQUEUE_ELEMENT_NAME
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

class ReplayFile(object):
    def __init__(self, pipeline):
        """ Replay a file on EOS """
        self.eos_count = 0
        self.pipeline = pipeline

        # Attach sink probe on file source
        filesrc = pipeline.get_by_name(FILESRC_ELEMENT_NAME)
        sink_pad = filesrc.get_static_pad("src")
        sink_pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.event)

    def event(self, pad, info):
        """ Process an event """
        event_type = info.get_event().type
        print("Event: ", event_type)
        if event_type != Gst.EventType.EOS:
            return Gst.PadProbeReturn.OK
        self.eos_count += 1
        if self.eos_count > 1:
            print("EOS Count: ", self.eos_count, " - Restarting")
            self.pipeline.set_state(Gst.State.PAUSED)
            self.pipeline.seek(1.0, Gst.Format.TIME,
                Gst.SeekFlags.KEY_UNIT | Gst.SeekFlags.FLUSH,
                Gst.SeekType.SET, 0.0 , Gst.SeekType.NONE, -1)
            self.pipeline.set_state(Gst.State.PLAYING)
            return Gst.PadProbeReturn.DROP
        return Gst.PadProbeReturn.OK
