/**
 * Main entrypoint (router) for webpage. Routes based on the anchor:
 *  1. #producer: video production page
 *  2. default/anything else: video streaming page
 * 
 * Set up the Vue application composed of either a Producer or Streamer of video that are rendered
 * optionally via v-if/v-else statements in the template.
 * 
 * @author LeStarch 
 */
import { createApp } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import ProducerControl from "./vue/producer.js"
import StreamerControl from "./vue/streamer.js"

// Vue JS
let app = createApp({
    template: "#app-template",
    components: {ProducerControl, StreamerControl},
    data() {
        return {route: window.location.hash.replace("#", "")};
    }
});


/**
 * Main function:
 *   1. Routes between producer and streamer
 *   2. Sets up button click event listeners
 * Hi Lewis!!
 */
function main() {
    app.mount("#app");
}
main();