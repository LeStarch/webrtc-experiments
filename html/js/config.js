VIDEO_SOURCE_COUNT=41;
VIDEO_SOURCE_STRING="scale";
VIDEO_SOURCES = [];
// Add video sources
for (let i = 0; i < VIDEO_SOURCE_COUNT; i++) {
    VIDEO_SOURCES.push(VIDEO_SOURCE_STRING + ("" + (i + 1)).padStart(3, "0"));
}
VIDEOS_HORIZONTAL=Math.ceil(Math.sqrt(VIDEO_SOURCE_COUNT));
VIDEO_WIDTH=Math.round(100/VIDEOS_HORIZONTAL * 9/16);