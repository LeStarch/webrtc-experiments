
import { createAnswer } from "../lib/rtc.js";
import { initial_select_text, streamer_template } from "./streamer-template.js"
import { sendAnswer } from "../lib/fetcher.js"
import { setupPeerData } from "./peer-helper.js"
import {Detector} from "../lib/detector.js";

export default {
    template: streamer_template,
    props: {
        stream: {
            type: String,
            default: null
        }
    },
    data() {
        let data = setupPeerData();
        Object.assign(data, {
            streams: null,
            selected: initial_select_text,
            poll_id: null,
            answered: false,
            ready: false
        });
        return data;
    },
    mounted() {
        Detector.singleton().addCallback(this);
        // Video handling
        let video_element = this.$el.querySelector(".video");
        this.peer.addEventListener('track', async (event) => {
            console.log("Detected new stream");
            const [remoteStream] = event.streams;
            video_element.srcObject = remoteStream;
        });
    },
    computed: {
        playable() {
            return this.ready && !this.answered;
        }
    },
    methods: {
        async streamRemote() {
            console.assert(
                ((this.selected != initial_select_text) && this.selected.offer),
                `Invalid stream selected: ${this.selected}`
            );
            // Prevent problems after assertion
            if (!this.selected?.offer) {
                return;
            }
            this.remote_id = this.selected.offerer;

            // Produce an answer
            let answer = await createAnswer(this.peer, this.selected.offer);
            this.answered = await sendAnswer(this.selected.offerer, this.peer_id, answer);
            if (this.answered) {
                clearInterval(this.poll_id);
                this.poll_id = null;
            }
        },
        updateOffers(streams) {
            this.streams = streams;
            if ((this.stream != null) && (this.selected === initial_select_text)) {
                let labels = this.streams.map(item => item.label);
                let stream_index = labels.indexOf(this.stream);
                if (stream_index !== -1) {
                    this.ready = true;
                    this.selected = this.streams[stream_index];
                }
            }
        }
    }
}