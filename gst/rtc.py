""" Handles WebRTC processing functions

Links the GStreamer WebRTC implementation to the REST-like messanger side channel through the
defined WebRTC object.

@author lestarch
"""
import logging


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
gi.require_version('GstWebRTC', '1.0')
from gi.repository import GstWebRTC
gi.require_version('GstSdp', '1.0')
from gi.repository import GstSdp

from .messaging import Messenger
from .pipeline import WEBRTC_ELEMENT_NAME

LOGGER = logging.getLogger(__name__)


class WebRTC(object):
    """ WebRTC to messaging channel bridge object
    
    WebRTC requires a side-channel for passing offers, answers, and ICE candidate connections
    between WebRTC clients. This object bridges the GStreamer `webrtcbin` element to the 
    messanger's REST-like interface for WebRTC messages. This is done by attaching GStreamer
    events to local functions, and handling POLLing callbacks.
    """
    def __init__(self, pipeline, messenger: Messenger):
        """ Construct the WebRTC bridge object
        
        Constructs the WebRTC bridge object between the given GStreamer pipeline and the given
        messanger object. This also registers two event handlers: 'on-negotiation-needed' that
        triggers the start of the WebRTC offer exchange, and 'on-ice-candidate' that triggers
        when a new ICE candidate mssage needs to be handled.

        Args:
            pipeline: GStreamer pipeline object containing a properly named `webrtcbin` element
            messenger: REST-like messaging API handler
        """
        self.webrtc = pipeline.get_by_name(WEBRTC_ELEMENT_NAME)
        self.offer_message = None
        self.webrtc.connect('on-negotiation-needed', self.on_negotiation_needed)
        self.webrtc.connect('on-ice-candidate', self.send_ice_candidate_message)
        self.webrtc.connect('on-new-transceiver', self.on_new_transceiver)
        self.webrtc.connect('on-data-channel', self.on_data_channel)
        self.messenger = messenger

    def on_negotiation_needed(self, element) -> None:
        """ Produce an offer in response to a negotiation needed event

        Once negotiation is ready to proceed, a WebRTC offer needs to be made to the remote peer.
        This offer is created and sent once it is produced.
    
        Args:
            element: webrtc gstreamer element
        """
        LOGGER.debug("Starting WebRTC negotiations")
        promise = Gst.Promise.new_with_change_func(self.on_offer_created, element, None)
        element.emit('create-offer', None, promise)

    def on_offer_created(self, promise, _, __) -> None:
        """ Transmit offer via side channel
        
        Wait for the supplied promise to be completed, then send the resultant offer to the remote
        client using the messenger. The offer is also set as the WebRTC local description.

        Args:
            promise: promise whose reply will contain the offer
            _: unused
            __: also unused
        """
        promise.wait()
        LOGGER.debug("Creating WebRTC offer")
        reply = promise.get_reply()  # MUST be a separate variable to keep data alive
        offer = reply.get_value("offer")
        promise = Gst.Promise.new()
        self.webrtc.emit('set-local-description', offer, promise)
        promise.interrupt() # Don't wait up for this promise
        self.messenger.send_offer(offer, self.on_answer, self.on_ice_received)

    def on_answer(self, answer_text: str) -> None:
        """ Receive an answer via side channel
        
        Receive a WebRTC answer from the messaging server and process it into the remote
        description for the `webrtcbin` GStreamer element.

        Args:
            answer_text: WebRTC answer in text form. Will be reconstructed into an object.
        """
        LOGGER.debug("Answer text: %s", answer_text)
        _, sdp = GstSdp.SDPMessage.new()
        GstSdp.sdp_message_parse_buffer(bytes(answer_text.encode()), sdp)
        answer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.ANSWER, sdp)

        promise = Gst.Promise.new()
        self.webrtc.emit('set-remote-description', answer, promise)
        promise.interrupt() # Don't wait up for this promise

    def on_ice_received(self, sdpMLineIndex: int, candidate: str) -> None:
        """ Receive an ICE message
        
        Receive an ICE candidate message from the REST-like messaging server and add it to the
        `webrtcbin` element of the GStreamer pipeline. The message comes in two parts: a line
        index and a candidate message as text.

        Args:
            sdpMLineIndex: sdb line index
            candidate: ICE candidate message
        """
        LOGGER.debug("ICE candidate index: %d and text: %s", sdpMLineIndex, candidate)
        self.webrtc.emit('add-ice-candidate', sdpMLineIndex, candidate)

    def send_ice_candidate_message(self, _, index: int, candidate: str) -> None:
        """ Send ICE candidate message to messaging server
        
        Sends ICE candidate message produced locally to the REST-like messaging server to be polled
        by the remote candidate.

        Args:
            _: unused
            index: line index of candidate
            candidate: ICE candidate message
        """
        self.messenger.send_ice(index, candidate)

    def on_new_transceiver(self, _, __, ___):
        LOGGER.warning("----- On NEW TRANSCEIVER -----")

    def on_data_channel(self, _, __, ___):
        LOGGER.warning("----- On DATA CHANNEL-----")
