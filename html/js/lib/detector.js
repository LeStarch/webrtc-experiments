/**
 * detector.js:
 *
 * Class used to poll for offers and act as a central database for holding the
 * available offers to the system.
 */
import {pollOffers} from "./fetcher.js";
import {setListInPlace} from "./util.js";

/**
 * Detector: polls for new offers and keeps the data available for clients
 * to poll.
 */
export class Detector {
    static _singleton = null;
    /**
     * Singleton creator methods.
     * @returns {null}: detector singleton
     */
    static singleton() {
        // Build singleton on the fly
        if (Detector._singleton == null) {
            Detector._singleton = new Detector();
        }
        return Detector._singleton;
    }

    /**
     * Setup detector and start polling.
     */
    constructor() {
        let _ = setInterval(this.updateOffers.bind(this), 1000);
        this.streams = [];
        this.callbacks = [];
    }

    /**
     * Update offers by polling
     * @returns {Promise<void>}
     */
    async updateOffers() {
        let [success, offers] = await pollOffers();
        if (success && offers) {
            let changed = setListInPlace(this.streams, offers);
            if (changed) {
                this.callbacks.forEach((item) => {
                    item.updateOffers(this.streams);
                });
            }
        }
    }

    /**
     * Add item to callback list.
     * @param item: item to add
     */
    addCallback(item) {
        this.callbacks.push(item);
    }
}