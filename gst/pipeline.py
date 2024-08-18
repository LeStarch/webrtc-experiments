""" GStreamer pipeline functions

Provides the functions and definitions used to setup the GStreamer pipeline. This pipeline consists
of two streams (audio and video) that are packed into an RTP payload before being pushed into a
webrpcbin element.

@author lestarch
"""
import logging


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


LOGGER = logging.getLogger(__name__)


WEBRTC_ELEMENT_NAME = "webrtcsender"


TEST_PIPELINE = f'''
videotestsrc is-live=true pattern=ball !
    videoconvert                       !
    vencoder_queue.
audiotestsrc is-live=true              !
    audioconvert                       !
    audioresample                      !
    aencoder_queue.
'''

DEVICE_PIPELINE = f'''
v4l2src                                    !
    video/x-raw,format=YUY2,framerate=15/1 !
    videoconvert                           !
    vencoder_queue.
alsasrc device=hw:2,0 !
    audioconvert !
    audioresample !
    aencoder_queue.
'''


BASE_PIPELINE_DESC = f'''
webrtcbin name={WEBRTC_ELEMENT_NAME} latency=0
queue name=vencoder_queue !
        x264enc tune=zerolatency bitrate=600 speed-preset=ultrafast key-int-max=15 !
        video/x-h264, profile=constrained-baseline !
        h264parse !
        rtph264pay aggregate-mode=zero-latency config-interval=-1 !
        application/x-rtp,media=video,encoding-name=H264,payload=96 !
        queue !
        {WEBRTC_ELEMENT_NAME}.
queue name=aencoder_queue !
        opusenc !
        rtpopuspay !
        queue ! application/x-rtp,media=audio,encoding-name=OPUS !
        {WEBRTC_ELEMENT_NAME}.
'''


def setup_pipeline(stream_type:str):
    """ Setup the GStreamer pipline with given stream choice
    
    Initializes GSTreamer libraries, parses the pipleine with the chose source fragment, and
    returns the pipeline to the caller.

    Several pipelines can be chosen:
        1. Test Pipeline: uses test sources for a quick test of the system
        2. Device Pipeline: uses video4linux and alsa to pull in web cam settings

    In order to ensure that WebRTC is configured before streamining, this function does not start
    the pipeline.
        
    Args:
        stream_type: one of "device" or "test" for the pipeline source to use

    Returns:
        initialized but on started pipeline
    """
    Gst.init(None)
    LOGGER.debug("Initializing GStreamer (%d.%d) with stream type: %s", Gst.version().major,
                 Gst.version().minor, stream_type)
    if stream_type == "test":
        chosen_pipeline = TEST_PIPELINE
    elif stream_type == "device":
        chosen_pipeline = DEVICE_PIPELINE
    else:
        assert False, f"Invalid stream choice: {stream_type}"
    pipeline = Gst.parse_launch(f"{BASE_PIPELINE_DESC}\n{chosen_pipeline}")
    return pipeline
