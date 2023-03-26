import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

gi.require_version('GstWebRTC', '1.0')
from gi.repository import GstWebRTC

gi.require_version('GstSdp', '1.0')
from gi.repository import GstSdp

class WebRTCException(Exception):
    pass

H264_PAYLOAD = 0
OPUS_PAYLOAD = 0


def extract_payload(sdpmsg, pipeline):
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
    videofilter = pipeline.get_by_name('videofilter')
    caps = videofilter.props.caps.copy()
    caps.set_value('payload', H264_PAYLOAD)
    videofilter.props.caps = caps
    print("Detected H264 payload={} and OPUS payload={}".format(H264_PAYLOAD, OPUS_PAYLOAD))

class WebRTC(object):
    """ Class to handle WebRTC interactions with the GStreamer pipeline"""
    def __init__(self, stage, pipeline):
        """ Given a stage, setup WebRTC handling
        
        Takes in a GStreamer stage specifically of type (webrpc) and use it
        to handle the incoming WebRPC requests.

        Args:
            stage: stage of the GStreamer pipeline to handle
        """
        assert stage.__class__.__name__.endswith("GstWebRTCBin"), "GSTreamer stage must be of type 'GstWebRTCBin'"
        self.stage = stage
        self.pipeline = pipeline

    def handleOffer(self, offer):
        """ Handle the given offer and given an answer

        Handles the given WebRTC offer and produces an aswer to the offer.

        Args:
            offer: offer from an out-of-band communications broker (e.g. flask)
        
        Return:
            answer to send back through broker
        """
        if not "sdp" in offer or offer.get("type", None) != "offer":
            raise WebRTCException("Offer from client is Malformed")
        _, message = GstSdp.SDPMessage.new()
        GstSdp.sdp_message_parse_buffer(bytes(offer['sdp'].encode()), message)
        extract_payload(message, self.pipeline)
        parsed_offer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.OFFER, message)
        promise = Gst.Promise.new_with_change_func(self.onOffer, None, None)
        self.stage.emit('set-remote-description', parsed_offer, promise)
    
    def onAnswer(self, promise, _, __):
        """ Handle anwser creation
        
        """
        print("[INFO] Producing answer!")
        promise.wait()
        answer = promise.get_reply().get_value("answer")

        local_promise = Gst.Promise.new()
        self.stage.emit('set-local-description', answer, local_promise)
        print("Interrupting")
        local_promise.wait() # Why?
        print("[INFO] Produced answer!")
        print(answer)
        print(dir(answer))
        print(answer.type)
        answer_data = {"type": "answer", "sdp": answer.sdp_as_text()}



    def onOffer(self, _, __, ___):
        """ Handles offer set message

        Args:
            promise: promise when offer is set
        """
        print("[INFO] Handling offer!")
        promise = Gst.Promise.new_with_change_func(self.onAnswer, self, None)
        self.stage.emit("create-answer", None, promise)