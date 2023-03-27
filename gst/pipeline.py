import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


WEBRTC_ELEMENT_NAME = "webrtcsender"


PIPELINE_DESC = f'''
webrtcbin name={WEBRTC_ELEMENT_NAME} bundle-policy=max-compat
    v4l2src device=/dev/video0 !
        video/x-raw,format=YUY2,framerate=15/1 !
        videoconvert !
        queue ! \
        x264enc tune=zerolatency speed-preset=ultrafast key-int-max=30 intra-refresh=true !
        video/x-h264, profile=(string)baseline, level=(string)3.1 !
        rtph264pay aggregate-mode=zero-latency config-interval=-1 !
        queue !
        application/x-rtp,media=video,encoding-name=H264 !
        {WEBRTC_ELEMENT_NAME}.
    alsasrc device=hw:2,0 !
        audioconvert !
        audioresample !
        queue !
        opusenc !
        rtpopuspay !
        queue ! application/x-rtp,media=audio,encoding-name=OPUS !
        {WEBRTC_ELEMENT_NAME}.
'''


def setup_pipeline():
    Gst.init(None)
    pipeline = Gst.parse_launch(PIPELINE_DESC)
    #self.webrtc.connect('on-data-channel', self.on_data_channel_created)
    return pipeline
