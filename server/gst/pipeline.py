import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

WEBRTC_ELEMENT_NAME = "webrtcsender"

PIPELINE_DESC = f'''
webrtcbin name={WEBRTC_ELEMENT_NAME} bundle-policy=max-compat
 videotestsrc is-live=true ! videoconvert !
 nvh264enc ! video/x-h264, profile=(string)baseline, level=(string)3.1 ! rtph264pay !
 queue ! capsfilter name=videofilter caps=application/x-rtp,media=video,encoding-name=H264 ! {WEBRTC_ELEMENT_NAME}.
'''


def setup_pipeline():
    Gst.init(None)
    pipeline = Gst.parse_launch(PIPELINE_DESC)
    #self.webrtc.connect('on-data-channel', self.on_data_channel_created)
    return pipeline