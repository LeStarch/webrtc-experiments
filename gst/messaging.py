import logging
import requests
import json

import asyncio

from functools import partial

LOGGER = logging.getLogger(__name__)

class Messanger(object):
    def __init__(self, host: str, label="GStreamer"):
        """"""
        self.host = host
        self.client_id = "yomama"
        self.label = label
        self.answer_cb = None
        self.remote_id = None
        self.seen_candidates = set()

    def send_offer(self, offer, answer_cb, ice_cb):
        """"""
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

    def send_ice(self, index, candidate):
        """"""
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
        """ """
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

    def poll_ice(self):
        """ POLL ICE """
        if self.remote_id is None or self.ice_cb is None:
            return None
        try:
            response = requests.get(f"{self.host}/ice/{self.client_id}")
            response.raise_for_status()
            data_packet = response.json()
            ice_messages = data_packet.get("messages", [])
            ice_messages = [(ice_message.get("sdpMLineIndex", None), ice_message.get("candidate", None)) for ice_message in ice_messages]
            ice_messages = [(index, candidate) for index, candidate in ice_messages if index is not None and candidate is not None]
            ice_messages = [ice_tuple for ice_tuple in ice_messages if ice_tuple not in self.seen_candidates]
            if ice_messages:
                LOGGER.info("Received %d ICE candidate messages from %s", len(ice_messages),
                            self.remote_id)
            for index, candidate in ice_messages:
                self.ice_cb(index, candidate)
                self.seen_candidates.add((index, candidate))
        except Exception as exc:
            LOGGER.warn("Failed to poll ice: %s", str(exc))

    async def poll(self):
        while True:
            await asyncio.sleep(1)
            self.poll_answer()
            self.poll_ice()