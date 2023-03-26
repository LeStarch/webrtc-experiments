/**
 * Code to wrap the primary steps of the WebRTC peer-to-peer API. Nominally this API is used here
 * to transmit video streams from one client to another client. The general steps break down as
 * follows:
 * 
 * Client 1:
 *   - Create peer connection description
 *   - Create offer data object
 *   - Attach offer as peer's local description
 *   - Send offer to remote client via side channel
 *   - Receive answer from remote client via side channel
 *   - Set answer as peer's remote description 
 * 
 * Client 2:
 *   - Create peer connection description
 *   - Receive offer data object
 *   - Set offer as peer's remote description
 *   - Create answer data object
 *   - Attach anwerr as peer's local description
 *   - Send answer to remote client via side channel
 *
 * Video Producing Client (Either 1 or 2 above):
 * - Attach media tracks to peer
 * 
 * Video Rendering Client (Either 1 or 2 above):
 * - Extract tracks from peer and render
 * 
 * Note: theoretically either client can be the video source and the other the video renderer. This
 * has not been tested as this demo only used the offerer as the video source and the answerer as
 * the video renderer.
 * 
 * @author LeStarch
 */

/**
 * Create a WebRTC peer object and unique client ID
 * 
 * Creates the WebRTC peer connection object used to create offers, answers, candidate events, and
 * any other WebRTC actions. This peer is paired with a pseudo-unique client ID used when
 * interacting with the side channel used to send WebRTC messages. 
 * 
 * @returns {Array[RTCPeerConnection, string]}: Array [WebRTC peer connection, uniqued ID string]
 */
export function createPeerConnection() {
    const configuration = {'iceServers': []}
    const peer = new RTCPeerConnection(configuration);
    return [peer, (new Date().getTime()).toString()];
}
/**
 * Attach tracks from a media stream to a peer connection
 * 
 * In order to send local media data from this client a remote client (for rendering) the tracks
 * are added to this client's peer object. They can then be extracted on the remote side.
 * 
 * @param {RTCPeerConnection} peer: peer connection to annotate
 * @param {MediaStream} stream: stream supplying media tracks
 */
export function attachTracks(peer, stream) {
    stream.getTracks().forEach(track => {
        peer.addTrack(track, stream);
    });
}

/**
 * Create a WebRTC offer to supply to a remote client
 * 
 * WebRTC offers start off the WebRTC connection between peers. The offer data is set as the
 * description of the local WebRTC peer and then transmitted via a side-channel to the remote peer
 * as the remote description. The offer returned from this function should be routed through some
 * channel to the remote client.
 * 
 * Note: this is an asynchronous function.
 * 
 * @param {RTCPeerConnection} peer: peer connection object of this client
 * @returns {RTCSessionDescriptionInit}: offer data send to the remote client
 */
export async function createOffer(peer) {
    const offer = await peer.createOffer();
    await peer.setLocalDescription(offer);
    return offer;
}

/**
 * Create a WebRTC answer to supply to a remote client in response to an incoming offer
 * 
 * WebRTC answers continue the WebRTC connection between peers. The incoming offer is set as this
 * client's remote description and then an answer is created. This answer data is set as the local
 * description of this WebRTC peer and then transmitted via a side-channel to the remote peer that
 * created the offer used as the remote description. The remote peer sets its remote description
 * from the returned answer.
 * 
 * Note: this is an asynchronous function.
 * 
 * @param {RTCPeerConnection} peer: peer connection object of this client
 * @param {RTCSessionDescriptionInit} offer: offer used as this client's remote description  
 * @returns {RTCSessionDescriptionInit}: answer data send to the remote client
 */
export async function createAnswer(peer, offer) {
    const remote_description = new RTCSessionDescription(offer)
    peer.setRemoteDescription(remote_description);
    const answer = await peer.createAnswer();
    await peer.setLocalDescription(answer);
    return answer;
}

/**
 * Set this peer's remote description from a given answer
 * 
 * WebRTC answers are used as the remote description on a peer that previously produced a WebRTC
 * offer. This answer comes in from some side-channel and is set as a property of the local peer.
 * 
 * @param {RTCPeerConnection} peer: peer connection object of this client
 * @param {RTCSessionDescriptionInit} answer: answer used as this client's remote description  
 */
export async function handleAnswer(peer, answer) {
    const remote_description = new RTCSessionDescription(answer);
    await peer.setRemoteDescription(remote_description);

}