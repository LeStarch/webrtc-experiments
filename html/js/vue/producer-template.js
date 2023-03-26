/**
 * Template code (HTML) used for the video producer component.
 * 
 * @author LeStarch
 */

// Initial text for within the select drop-down
export let initial_select_text = "Select Video Device";

/**
 * Video production component used to annotate a stream with an ID, and select the local video
 * device to stream to the remote client.
 */
export let producer_template = `
<div>
    <h2>Video Production: {{ peer_id }}</h2>
    <button @click="detectDevices">Detect Video</button>
    <label for="device-sel" class="offer-control">Source Select:</label>
    <select v-model="selected" @change="offerDevice">
        <option disabled>${initial_select_text}</option>
        <option v-for="device in devices" :value="device">
            {{ device.label || device.deviceId }}
        </option>
    </select>
    <input type="text" v-model="stream_id" />
    <h3>Streaming -
        <span v-if="answered" style="font-color: green;">ON</span>
        <span v-else  style="font-color: red;">OFF</span>
    </h3>
</div>
`;