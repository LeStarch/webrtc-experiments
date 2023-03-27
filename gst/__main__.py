
import logging
import time

import asyncio

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
    messenger = Messanger("http://127.0.0.1:5000")
    webrtc = WebRTC(pipeline, messenger)
    pipeline.set_state(Gst.State.PLAYING)

    try:
        asyncio.run(messenger.poll())
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    main()
