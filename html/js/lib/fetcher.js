/**
 * Code to wrap the fetch API to handle asynchronous remote requests. Once upon a time this was 
 * done in ajax. This allows several methods to query the remote. Data is passed in JSON, and
 * when a bad status comes back errors are logged.
 * 
 * Expected format of responses:
 * 
 * {
 *     "status": <some message>,
 *     ...data... 
 * }
 * 
 * @author LeStarch
 */

/**
 * Perform HTML action (method) with given data to gievn server URL
 * 
 * Request data from the remote server. Can specify url, method, and message to send. Method
 * defaults to "GET" and message defaults to unset.
 * 
 * @param url: URL to fetch using fetch API 
 * @param method: "GET", "POST", etc. Default: "GET"
 * @param data: data to yeet to the server. Default: unse
 * @returns: Array [status, returned data]
 */
async function requestor(url, method, data) {
    // Base data structure
    let fetch_data = {
        method: (method) ? method : "GET",
        cache: "no-cache",
        body: (data) ? JSON.stringify(data) : undefined,
        headers: {
            "Content-Type": "application/json",
        },
    }
    // Fetch data, await response
    let response = await fetch(url, fetch_data);
    let response_data = await response.json();
    if (!response.ok) {
        console.error(response_data.status || "Unknown fetching error");
        return [false, {}];
    }
    return [true, response_data];
}

/**
 * POST an offer from this client via the backend server
 * 
 * WebRTC requires handling of setup messages via a side channel. This passes the "offer" type
 * message through this side channel. Stream ID is the human readable message identifying the
 * stream, offer id is to track this "client" as the offerer, and offer is the peer-produced
 * offer data.
 * 
 * Note: this function is asynchronous
 * 
 * @param {string} stream_id: human-readable stream ID   
 * @param {string} offer_id: unique ID representing this "offering" client
 * @param {Object} offer: offer data from WebRTC
 * @returns: success/failure of remote call
 */
export async function sendOffer(stream_id, offer_id, offer) {
    let [success, _] = await requestor(
        "/make-offer", "POST", {"label": stream_id, "offerer": offer_id, "offer": offer}
    );
    return success;
}

/**
 * POST an answer from this client via the backend server
 * 
 * WebRTC requires handling of setup messages via a side channel. This passes the "answer" type
 * message through this side channel. Offer ID is the human readable message identifying the
 * offer client to whom this answer is a response, answerwe is the ID of this answering client,
 * and answer is the answer data object.
 * 
 * Note: this function is asynchronous
 * 
 * @param {string} offer_id: human-readable offer client ID   
 * @param {string} answerer: unique ID representing this "answering" client
 * @param {Object} offer: offer data from WebRTC
 * @returns: success/failure of remote call
 */
export async function sendAnswer(offer_id, answerer, answer) {
    let [success, _] = await requestor(
        "/make-answer", "POST", {"offerer": offer_id, "answerer": answerer, "answer": answer}
    );
    return success;
}

/**
 * POST ICE candidate messages from this client via the side channel
 * 
 * This function is for POSTing ICE messages with association to the current client. Remote
 * clients are expected to have determined this candidate client ID and poll for the messages
 * such that this client need not know its remote at the time that these messages are POSTed.
 * 
 * ICE messages represent candidate communication channels between WebRTC clients. These messages,
 * passed through the side channel, allow the WebRTC clients to connect directly across unknown
 * network and internet topologies.
 * 
 * Note: this function is asynchronous
 * 
 * @param {string} client_id: answerer or offerer ID to of this client
 * @param {object} candidate: WebRTC event-produced candidate information 
 * @returns: success/failure of remote call
 */
export async function sendIce(client_id, candidate) {
    let [success, _] = await requestor("/ice/" + client_id, "POST", candidate);
    return success;
}

/**
 * POLL for answers to the given offering client
 * 
 * POLL for WebRTC answers to a previous offer made with the offer ID. The offer ID is of this
 * client and as such the calling client must have previously made an offer before this call could
 * produce any answer. Polling should begin after an offer to ensure timely reception of a message.
 * 
 * Note: this function is asynchronous
 *
 * @param {string} offer_id: ID of client which made previous answer
 * @returns: Array [success/failure of remote call, ID of answering client, returned answer data]
 */
export async function pollAnswer(offer_id) {
    let [success, data] = await requestor(`/answer/${offer_id}`);
    return [success, data.answerer || "", data.answer || {}]
}

/**
 * POLL for offers from remote clients
 * 
 * POLL for WebRTC offers made from any remote client. Return a list of offers sent via the side
 * channel to this client.  These offers are not limited to a single client.
 *
 * Note: this function is asynchronous
 * 
 * @returns Array [success/failure of remote call, list of offer objects]
 */
export async function pollOffers() {
    let [success, data] = await requestor(`/offers`);
    return [success, data.offers || []];
}

/**
 * POLL for ICE candidate messages from remote client via side channel
 * 
 * This function is for GETing ICE messages from a given remote client that has previously POSTed
 * its candidate messages.
 * 
 * ICE messages represent candidate communication channels between WebRTC clients. These messages,
 * passed through the side channel, allow the WebRTC clients to connect directly across unknown
 * network and internet topologies.
 * 
 * Note: this function is asynchronous
 * 
 * @param {string} remote_id:: answerer or offerer ID to of the remote client
 * @returns: Array [success/failure of remote call, list of ICE candidate messages]
 */
export async function pollIce(remote_id) {
    let [success, ice] = await requestor("/ice/" + remote_id, "GET");
    return [success, ice.messages || []];
}