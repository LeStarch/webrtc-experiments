import argparse
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


BASE_URL = "http://127.0.0.1:5000/" 

def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser(description="Host the WebRPC GStreamer backend")
    return parser.parse_args()


def main():
    """ Hi Lewis!!! """
    _ = parse_args()
    pipeline = setup_pipeline()
    messenger = Messanger(BASE_URL)
    print(f"[INFO] Stream: {BASE_URL}")
    print(f"[INFO] Produce: {BASE_URL}#produce")
    webrtc = WebRTC(pipeline, messenger)
    pipeline.set_state(Gst.State.PLAYING)

    try:
        asyncio.run(messenger.poll())
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
