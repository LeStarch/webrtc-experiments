
import logging
import time

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from .pipeline import setup_pipeline
from .messaging import Messanger
from .rtc import WebRTC


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.debug("Logging initialized: %d.%d", Gst.version().major, Gst.version().minor)



def main():
    """ Hi Lewis!!! """
    pipeline = setup_pipeline()
    messenger = Messanger()
    webrtc = WebRTC(pipeline, messenger)
    pipeline.set_state(Gst.State.PLAYING)

    time.sleep(10)


if __name__ == "__main__":
    main()