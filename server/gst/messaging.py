import logging
import requests
import json

LOGGER = logging.getLogger(__name__)

class Messanger(object):

    def send_offer(self, offer):
        """"""
        LOGGER.debug("Attempting to send offer")
        print(dir(offer.sdp))
        #offer_text = offer.sdp.as_text()
        LOGGER.info("Sending offer: %s", offer_text)

        print(offer_text)