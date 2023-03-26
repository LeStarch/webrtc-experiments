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
        LOGGER.debug("Starting negotiations")
        promise = Gst.Promise.new_with_change_func(self.on_offer_created, element, None)
        element.emit('create-offer', None, promise)

    def on_offer_created(self, promise, _, __):
        """ Transmit offer via sife channel"""
        promise.wait()
        LOGGER.debug("Making WebRTC offer")
        offer = promise.get_reply().get_value("offer")
        self.messenger.send_offer(offer)

        #new_promise = Gst.
        #self.webrtc.emit('set-local-description', offer, None)

        #self.send_sdp_offer(offer)


    def send_ice_candidate_message(self):
        print("FUCK NEED ICE")
