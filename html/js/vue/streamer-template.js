
/**
 * Template code (HTML) used for the video consumer component.
 * 
 * @author LeStarch
 */

// Initial text for within the select drop-down
export let initial_select_text = "Select Remote Stream";

/**
 * Streamer template providing a video selection drop-down to control the selection of remote video
 * streams and a video tag for rendering the video from the WebRTC peer.
 */
export let streamer_template = `
<div style="width: 100%">
    <h4>{{ (stream != null) ? stream : peer_id }}</h4>
    <video class="video" autoplay playsinline controls="false"
        style="width: 100%; border: 1px solid black;">
    </video>
    <div>
        <span v-if="stream == null">
            <label for="offer-sel">Stream Remote Video:</label>
            <select  v-model="selected" @change="streamRemote" :disabled="answered">
                <option disabled>${initial_select_text}</option>
                <option v-for="stream in streams" :value="stream">
                    {{ stream.label }}
                </option>
            </select>
        </span>
        <button v-else @click="streamRemote" :disabled="!playable">Play</button>
    </div>                
</div>
`;