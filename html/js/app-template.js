export let app_template = `
<div>
    <producer-control v-if="route == 'produce'"></producer-control>
    <streamer-control v-else-if="route == 'single'"></streamer-control>
    <div v-else v-for="source in configured_sources"
        style="display:inline-block; width: ${VIDEO_WIDTH}vw">
        <streamer-control v-bind:stream="source"></streamer-control>
    </div>
</div>
`;