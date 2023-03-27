import logging
LOGGER = logging.getLogger(__name__)

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
gi.require_version('GstWebRTC', '1.0')
from gi.repository import GstWebRTC
gi.require_version('GstSdp', '1.0')
from gi.repository import GstSdp

from .pipeline import WEBRTC_ELEMENT_NAME

class WebRTC(object):

    def __init__(self, pipeline, messenger):
        self.webrtc = pipeline.get_by_name(WEBRTC_ELEMENT_NAME)
        self.offer_message = None
        self.webrtc.connect('on-negotiation-needed', self.on_negotiation_needed)
        self.webrtc.connect('on-ice-candidate', self.send_ice_candidate_message)
        self.messenger = messenger

    def on_negotiation_needed(self, element):
        """ Produce an offer in response to a negotiation needed event

        Once negotiation is ready to proceed, a WebRTC offer needs to be made to the remote peer.
        This offer is created and sent once it is produced.
    
        Args:
            element: webrtc gstreamer element
        """
        LOGGER.debug("Starting WebRTC negotiations")
        promise = Gst.Promise.new_with_change_func(self.on_offer_created, element, None)
        element.emit('create-offer', None, promise)

    def on_offer_created(self, promise, _, __):
        """ Transmit offer via side channel"""
        promise.wait()
        LOGGER.debug("Creating WebRTC offer")
        reply = promise.get_reply()  # MUST be a separate variable to keep data alive
        offer = reply.get_value("offer")
        promise = Gst.Promise.new()
        self.webrtc.emit('set-local-description', offer, promise)
        promise.interrupt() # Don't wait up for this promise
        self.messenger.send_offer(offer, self.on_answer, self.on_ice_received)

    def on_answer(self, answer_text):
        """ Receive an answer via side channel """
        LOGGER.debug("Answer text: %s", answer_text)
        _, sdp = GstSdp.SDPMessage.new()
        GstSdp.sdp_message_parse_buffer(bytes(answer_text.encode()), sdp)
        answer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.ANSWER, sdp)

        promise = Gst.Promise.new()
        self.webrtc.emit('set-remote-description', answer, promise)
        promise.interrupt() # Don't wait up for this promise

    def on_ice_received(self, sdpMLineIndex, candidate):
        LOGGER.debug("ICE candidate index: %d and text: %s", sdpMLineIndex, candidate)
        self.webrtc.emit('add-ice-candidate', sdpMLineIndex, candidate)

    def send_ice_candidate_message(self, _, index, candidate):
        self.messenger.send_ice(index, candidate)