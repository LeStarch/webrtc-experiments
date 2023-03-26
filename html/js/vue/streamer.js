
import { createAnswer } from "../lib/rtc.js";
import { setListInPlace } from "../lib/util.js";
import { initial_select_text, streamer_template } from "./streamer-template.js"
import { pollOffers, sendAnswer } from "../lib/fetcher.js"
import { setupPeerData } from "./peer-helper.js"

export default {
    template: streamer_template,
    data() {
        let data = setupPeerData();
        Object.assign(data, {
            streams: [],
            selected: initial_select_text,
            poll_id: null,
            answered: false
        });
        return data;
    },
    mounted() {
        this.poll_id = setInterval(this.updateOffers.bind(this), 1000);

        // Video handling
        let video_element = this.$el.querySelector("#video");
        this.peer.addEventListener('track', async (event) => {
            console.log("Detected new stream");
            const [remoteStream] = event.streams;
            video_element.srcObject = remoteStream;
        });

    },
    methods: {
        async updateOffers() {
            let [success, offers] = await pollOffers();
            if (success && offers) {
                setListInPlace(this.streams, offers);
            }
        },
        async streamRemote() {
            console.assert(
                ((this.selected != initial_select_text) && this.selected.offer),
                `Invalid stream selected: ${this.selected}`
            );
            // Prevent problems after assertion
            if (!this.selected?.offer) {
                return;
            }
            this.remote_id = this.offerer;

            // Produce an answer
            let answer = await createAnswer(this.peer, this.selected.offer);
            this.answered = await sendAnswer(this.selected.offerer, this.peer_id, answer);
            if (this.answered) {
                clearInterval(this.poll_id);
                this.poll_id = null;
            }
        }
    }
}