import random
import logging
import os
import sys
import json
import argparse
import concurrent

ROOT = os.path.dirname(__file__)

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
gi.require_version('GstWebRTC', '1.0')
from gi.repository import GstWebRTC
gi.require_version('GstSdp', '1.0')
from gi.repository import GstSdp

H264_PAYLOAD = 0
OPUS_PAYLOAD = 0

PIPELINE_DESC = f'''
webrtcbin name=sendonly bundle-policy=max-compat
 videotestsrc is-live=true ! videoconvert !
 x264enc ! video/x-h264, profile=(string)baseline, level=(string)3.1 ! rtph264pay !
 queue ! capsfilter name=videofilter caps=application/x-rtp,media=video,encoding-name=H264 ! sendonly.
'''

class WebRTCClient:
    def __init__(self, id_, ws):
        self.id_ = id_
        self.pipe = None
        self.webrtc = None
        self.conn = ws

    def on_data_channel_error(self, error):
        print('channel error:%s' % error)

    def on_data_channel_open(self, channel):
        channel.emit('send-string', 'Hello from python webrtcbin!')

    def on_message_string(self, channel, msg):
        print('msg received')
        print(msg)

    def on_message_data(self, channel, data):
        print('data received')
        print(data)

    def on_data_channel_created(self, webrtcbin, channel):
        print('setting data event')
        channel.connect('on-open', self.on_data_channel_open)
        channel.connect('on-message-string', self.on_message_string)
        channel.connect('on-message-data', self.on_message_data)

    def send_sdp_message(self, type, data):
        msg = json.dumps({'type': type, 'sdp': data.sdp.as_text()})
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.conn.send_str(msg))
        loop.close()
    
    def on_answer_created(self, promise, _, __):
        promise.wait()
        reply = promise.get_reply()
        answer = reply.get_value('answer')
        promise = Gst.Promise.new()
        self.webrtc.emit('set-local-description', answer, promise)
        promise.interrupt()
        self.send_sdp_message('answer', answer)

    def on_offer_set(self, promise, _, __):
        promise = Gst.Promise.new_with_change_func(self.on_answer_created, self, None)
        self.webrtc.emit('create-answer', None, promise)

    def send_ice_candidate_message(self, _, mlineindex, candidate):
        icemsg = json.dumps({'candidate': {'candidate': candidate, 'sdpMLineIndex': mlineindex}})
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.conn.send_str(icemsg))
        loop.close()

    def extract_payload(self, sdpmsg):
        global H264_PAYLOAD, OPUS_PAYLOAD
        for m in range(0, sdpmsg.medias_len()):
            media = sdpmsg.get_media(m)
            for f in range(0, media.formats_len()):
                payload = media.get_format(f)
                if not payload.isnumeric():
                    # datachannel
                    break
                caps = media.get_caps_from_media(int(payload))
                if caps.get_size() < 1:
                    # empty caps
                    break
                struct = caps.get_structure(0)
                if (struct.get_string('encoding-name') == 'H264'):
                    H264_PAYLOAD = int(payload)
                    break
                elif (struct.get_string('encoding-name') == 'OPUS'):
                    OPUS_PAYLOAD = int(payload)
                    break
        videofilter = self.pipe.get_by_name('videofilter')
        caps = videofilter.props.caps.copy()
        caps.set_value('payload', H264_PAYLOAD)
        videofilter.props.caps = caps
        print("Detected H264 payload={} and OPUS payload={}".format(H264_PAYLOAD, OPUS_PAYLOAD))

    def start_pipeline(self):
        self.pipe = Gst.parse_launch(PIPELINE_DESC)
        self.webrtc = self.pipe.get_by_name('sendonly')
        self.webrtc.connect('on-ice-candidate', self.send_ice_candidate_message)
        self.webrtc.connect('on-data-channel', self.on_data_channel_created)
        self.pipe.set_state(Gst.State.PLAYING)

    def handle_sdp(self, data):
        assert (self.webrtc)
        msg = json.loads(data)
        if 'sdp' in msg and msg['type'] == 'offer':
            res, sdpmsg = GstSdp.SDPMessage.new()
            GstSdp.sdp_message_parse_buffer(bytes(msg['sdp'].encode()), sdpmsg)
            self.extract_payload(sdpmsg)
            offer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.OFFER, sdpmsg)
            promise = Gst.Promise.new_with_change_func(self.on_offer_set, None, None)
            self.webrtc.emit('set-remote-description', offer, promise)
        elif 'sdp' in msg and msg['type'] == 'answer':
            res, sdpmsg = GstSdp.SDPMessage.new()
            GstSdp.sdp_message_parse_buffer(bytes(msg['sdp'].encode()), sdpmsg)
            answer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.ANSWER, sdpmsg)
            promise = Gst.Promise.new()
            self.webrtc.emit('set-remote-description', answer, promise)
            promise.interrupt()
        elif 'candidate' in msg:
            ice = msg['candidate']
            candidate = ice['candidate']
            sdpmlineindex = ice['sdpMLineIndex']
            self.webrtc.emit('add-ice-candidate', sdpmlineindex, candidate)

    def close_pipeline(self):
        if self.pipe:
            self.pipe.set_state(Gst.State.NULL)
            self.pipe = None
        self.webrtc = None

def check_plugins():
    needed = ["opus", "vpx", "nice", "webrtc", "dtls", "srtp", "rtp", "sctp",
              "rtpmanager", "videotestsrc", "x264"]
    missing = list(filter(lambda p: Gst.Registry.get().find_plugin(p) is None, needed))
    if len(missing):
        print('Missing gstreamer plugins:', missing)
        return False
    return True


if __name__=='__main__':
    Gst.init(None)
    if not check_plugins():
        sys.exit(1)
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    start_pipeline()

