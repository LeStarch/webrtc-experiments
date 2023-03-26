/**
 * Code to wrap the media device functions for handling video data. Functions are implemented to
 * open local video devices on the client and to handle video data extracted from a remote (WebRTC)
 * connection.
 * 
 * Media devices may be enumerated, opened, and used as a source for media tracks that are attached
 * to WebRTC connection or rendered locally.
 * 
 * @author LeStarch
 */

/**
 * Enumerate local media devices that may be used as video sources.
 * 
 * List 'videoinput' devices that are attached locally to the current computer. Return the filtered
 * results to the caller.
 * 
 * Based on: https://webrtc.org/getting-started/media-devices
 * 
 * @returns {Array}: list of local "videoinput" devices
 */
export async function localVideoDevices() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    let video_devices = devices.filter(device => device.kind == "videoinput");
    return video_devices;
}

/**
 * Open a local media device by ID
 * 
 * Media devices must be opened before these can be used. This is done by providing constraints to
 * the getUserMedia function. The constraints provided here are the specific ID of the device that
 * will be opened.
 * 
 * @param {string} id: id of device to open
 * @returns {MediaStream}: media stream produced from the opened device
 */
export async function openLocalVideoDevice(id) {
    const constraints = {
        "video": {
            deviceId: id
    }};
    let open_device = await navigator.mediaDevices.getUserMedia(constraints);
    console.log("Opening device:");
    console.log(open_device);
    return open_device;
}
