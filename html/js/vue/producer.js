import { localVideoDevices, openLocalVideoDevice } from "../lib/video.js";
import { createPeerConnection, attachTracks, createOffer, handleAnswer } from "../lib/rtc.js";
import { setListInPlace } from "../lib/util.js";
import { initial_select_text, producer_template } from "./producer-template.js"
import { sendOffer, pollAnswer } from "../lib/fetcher.js"
import { setupPeerData } from "./peer-helper.js"

export default {
    template: producer_template,
    data() {
        let data = setupPeerData();
        Object.assign(data, {
            devices: [],
            selected: initial_select_text,
            stream_id: "Stream 1",
            poll_id: null,
            answered: false
        });
        return data;
    },
    methods: {
        /**
         * Detect video devices and update selection dialog
         */
        async detectDevices() {
            let new_devices = await localVideoDevices();
            setListInPlace(this.devices, new_devices);
        },

        /**
         * Offer video device via WebRTC
         */
        async offerDevice() {
            console.assert(
                ((this.selected != initial_select_text) && this.selected.deviceId),
                `Invalid device selected: ${this.selected}`
            );
            // Prevent problems after assertion
            if (!this.selected?.deviceId) {
                return;
            }
            // Open stream and attach it to the tracks
            let stream = await openLocalVideoDevice(this.selected.deviceId);
            attachTracks(this.peer, stream);
            let offer = await createOffer(this.peer);

            // Send an offer and look for an answer
            let success = await sendOffer(this.stream_id, this.peer_id, offer);
            if (success) {
                this.poll_id = setInterval(this.checkAnswer.bind(this), 1000);
            }
        },

        async checkAnswer() {
            let [success, answerer, answer] = await pollAnswer(this.peer_id);
            if (success && answerer && answer) {
                clearInterval(this.poll_id);
                this.remote_id = answerer;
                this.answered = true;
                handleAnswer(this.peer, answer);
            }
        }
    }
}