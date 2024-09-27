""" Messaging side-channel communicating with Flask server

WebRTC needs a side-channel for message passing outside the protocol. This application uses a flask
REST-like webserver to pass messages about. This file handles these functions. 

@author lestarch
"""
import asyncio
import logging
import requests
import time
from typing import Callable

LOGGER = logging.getLogger(__name__)


class Messenger(object):
    """ Object for controlling the REST-like API
    
    The side-channel REST-like API processing the following messages:

    1. Send Offer: sends WebRTC offers to the REST-like messaging server
    2. Send ICE: sends WebRTC ICE candidate messages to the REST-like messaging server
    3. Poll for Answer: polls for WebRTC answers that come into the REST-like messaging server
    4. Poll for ICE: polls for WebRTC ICE candidate messages that come into the server 
    """
    def __init__(self, host: str, label: str="GStreamer") -> None:
        """ Constructor for messaging
        
        Initialize the messaging connection with given host and lable for remote client.

        Args:
            host: host url as a string
            label: client label
        """
        self.host = host
        self.client_id = f"{round(time.time() * 1000)}"
        self.label = label
        self.answer_cb = None
        self.remote_id = None
        self.seen_candidates = set()

    def send_offer(self, offer, answer_cb: Callable, ice_cb: Callable) -> None:
        """ Send a WEbRTC offer
        
        Sends an WebRTC offer package with the supplied label, client id used by the messaging
        server and offer text. Takes callbacks for processing answers and ICE candidate messages
        that result from this offer.

        Args:
            offer: offer text to send to client
            answer_cb: callback used to process the answer to this offer
            ice_cb: callback to process ICE candidates from the answering clienit
        """
        LOGGER.info("Sending WebRTC offer")
        offer_text = offer.sdp.as_text()
        LOGGER.debug("Offer text: %s", offer_text)
        data_packet = {
            "label": self.label,
            "offerer": self.client_id,
            "offer": {"type": "offer", "sdp": offer_text}
        }
        try:
            response = requests.post(f"{self.host}/make-offer", json=data_packet)
            response.raise_for_status()
            self.answer_cb = answer_cb
            self.ice_cb = ice_cb
        except requests.exceptions.RequestException as exc:
            LOGGER.warning("Failed to send offer: %s %s", str(exc), response.text)

    def send_ice(self, index: int, candidate: str) -> None:
        """ Send ICE candidate messages
        
        ICE candidate messages consist of two parts, the sdpMLineIndex and the cadidate messages.
        These messages are POSTed to the server at the current client's address. The remote client
        is expected to POLL for these messages with the local client's ID.

        Args:
            index: sdpMLineIndex of the candidate message
            candidate: candidate message text
        """
        LOGGER.info("Sending WebRTC ice candidate")
        LOGGER.debug("Candidate index: %d text: %s", index, candidate)
        data_packet = {
            "sdpMLineIndex": index,
            "candidate": candidate
        }
        try:
            response = requests.post(f"{self.host}/ice/{self.client_id}", json=data_packet)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            LOGGER.warning("Failed to send ICE: %s %s", str(exc), response.text)

    def poll_answer(self):
        """ POLL for an answer to a previous offer
        
        POLLs for answers to a previous answer. Should an answer arrive, the `answer_cb` is called
        with the answer data, otherwise the function breaks early.
        """
        # Check we should be polling for an answer
        if self.answer_cb is None:
            return None

        try:
            response = requests.get(f"{self.host}/answer/{self.client_id}")
            response.raise_for_status()

            # Process response from server
            data_packet = response.json()
            answer = data_packet.get("answer", None)
            self.remote_id = data_packet.get("answerer", None)

            # No answer found yet
            if answer is None or self.remote_id is None:
                return

            # Attempt to process valid answer
            LOGGER.info(f"Received WebRTC answer from: %s", self.remote_id)
            self.answer_cb(answer.get("sdp", None))
            self.answer_cb = None
        except Exception as exc:
            LOGGER.warn("Failed to poll answer: %s", str(exc))

    def poll_ice(self) -> None:
        """ POLL for ICE candidate messages
        
        POLLs for ICE candidate messages from the remote client. If new messages were received,
        then these messages are passed to the `ice_cb` function. Otherwise the function breaks
        out early.
        """
        if self.remote_id is None or self.ice_cb is None:
            return None
        try:
            response = requests.get(f"{self.host}/ice/{self.remote_id}")
            response.raise_for_status()
            data_packet = response.json()
            ice_messages = data_packet.get("messages", [])
            # Process the messages into tuples that are non-None and have not been received before
            ice_messages = [
                (ice_message.get("sdpMLineIndex", None), ice_message.get("candidate", None))
                for ice_message in ice_messages
            ]
            ice_messages = [
                (index, candidate)
                for index, candidate in ice_messages
                if index is not None and candidate is not None
            ]
            ice_messages = [
                ice_tuple
                for ice_tuple in ice_messages
                if ice_tuple not in self.seen_candidates
            ]

            # Process new messages
            if ice_messages:
                LOGGER.info("Received %d ICE candidate messages from %s", len(ice_messages),
                            self.remote_id)
            for index, candidate in ice_messages:
                self.ice_cb(index, candidate)
                self.seen_candidates.add((index, candidate))
        except Exception as exc:
            LOGGER.warn("Failed to poll ice: %s", str(exc))

    async def poll(self):
        """ Repetitivly POLL for both ICE candidates and answers
        
        Polls on a 1 second bases for answers and ICE candidates in that order.
        """
        while True:
            await asyncio.sleep(1)
            self.poll_answer()
            self.poll_ice()
