""" Entrypoint for the `gst` module

Launches the GST pipeline and attaches it to the WebRTC handler and messagging system. Handles the
input arguments to launch the various peices.

@author lestarch
"""
import argparse
import asyncio
import logging


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


from .pipeline import setup_pipeline
from .messaging import Messenger
from .rtc import WebRTC


LOGGER = logging.getLogger(__name__)


def parse():
    """ Parse the arguments for the program
    
    Parse the arguments for the program, validate the inputs and return the arguments as a
    namespace for further usage. Initializes the logging routines with the supplied arguments.

    Returns:
        arguments as a namespace
    """
    parser = argparse.ArgumentParser(description="Setup a GStreamer to WebRTC bridge")
    parser.add_argument("-u", "--messaging-url", default="http://127.0.0.1:5000",
                       help="URL of the messaging server")
    parser.add_argument("-l", "--label", default="GStreamer",
                       help="Label the produced WebRTC stream set")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose/debugging output")
    parser.add_argument("-s", "--stream-type", choices=["test", "device"], default="test",
                        help="Set the type of the stream running to GStreamer")
    args = parser.parse_args()

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)
    return args

def main():
    """ Hi Lewis!!! """
    args = parse()

    pipeline = setup_pipeline(args.stream_type)
    messenger = Messenger(args.messaging_url, label=f"{args.label} - {args.stream_type}")
    webrtc = WebRTC(pipeline, messenger)
    
    try:
        # Stream the pipeline and start the message polling
        pipeline.set_state(Gst.State.PLAYING)
        asyncio.run(messenger.poll())
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    main()
