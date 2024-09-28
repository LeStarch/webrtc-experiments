""" Entrypoint for the `gst` module

Launches the GST pipeline and attaches it to the WebRTC handler and messagging system. Handles the
input arguments to launch the various peices.

@author lestarch
"""
import argparse
import asyncio
import logging
from pathlib import Path


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


from .pipeline import setup_pipeline
from .messaging import Messenger
from .rtc import WebRTC
from .replay import ReplayFile

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
    parser.add_argument("-s", "--stream-type", choices=["test", "device", "file"], default="test",
                        help="Set the type of the stream running to GStreamer")
    parser.add_argument("-f", "--file", help="Path to file (only used with -s file)", type=Path)
    args = parser.parse_args()
    if args.stream_type == "file" and (args.file is None or not args.file.exists()):
        raise TypeError("-f must be specified and must exist")
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)
    return args


def main():
    """ Hi Lewis!!! """
    args = parse()

    pipeline = setup_pipeline(args.stream_type, args.file)
    messenger = Messenger(args.messaging_url, label=f"{args.label}")
    webrtc = WebRTC(pipeline, messenger)
    replayer = ReplayFile(pipeline)
    try:
        # Stream the pipeline and start the message polling
        pipeline.set_state(Gst.State.PLAYING)

        async def async_main():
            await asyncio.gather(
                messenger.poll(),
            )
        asyncio.run(async_main())
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    main()
