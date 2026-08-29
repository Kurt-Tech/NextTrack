const contextSelect = document.getElementById("context-select");
const recentTracksContainer = document.getElementById("recent-tracks");
const statusMessage = document.getElementById("context-status");

let evaluationContexts = [];


async function loadEvaluationContexts() {
    try {
        statusMessage.textContent = "Loading listening contexts...";

        const response = await fetch("/evaluation/contexts");

        if (!response.ok) {
            throw new Error(
                `Failed to load contexts: ${response.status}`
            );
        }

        const data = await response.json();

        evaluationContexts = data.contexts;

        populateContextSelect(evaluationContexts);

        statusMessage.textContent =
            "Select a listening context to continue.";
    } catch (error) {
        console.error(error);

        statusMessage.textContent =
            "Unable to load listening contexts.";
    }
}


function populateContextSelect(contexts) {
    contextSelect.innerHTML = "";

    const placeholderOption =
        document.createElement("option");

    placeholderOption.value = "";
    placeholderOption.textContent =
        "Select a listening context";

    contextSelect.appendChild(
        placeholderOption
    );

    for (const context of contexts) {
        const option =
            document.createElement("option");

        option.value = context.id;
        option.textContent = context.name;

        contextSelect.appendChild(option);
    }

    contextSelect.disabled = false;
}


function displayRecentTracks(contextId) {
    recentTracksContainer.innerHTML = "";

    if (!contextId) {
        recentTracksContainer.innerHTML = `
            <p class="helper-text">
                Select a context to view the recent tracks.
            </p>
        `;

        return;
    }

    const context = evaluationContexts.find(
        item => item.id === contextId
    );

    if (!context) {
        recentTracksContainer.innerHTML = `
            <p class="error-text">
                Unable to find the selected context.
            </p>
        `;

        return;
    }

    const heading =
        document.createElement("h3");

    heading.textContent =
        `${context.name} Recent Tracks`;

    recentTracksContainer.appendChild(heading);

    const trackList =
        document.createElement("div");

    trackList.className = "track-list";

    for (const track of context.recent_tracks) {
        const trackCard =
            document.createElement("article");

        trackCard.className = "track-card";

        const trackName =
            document.createElement("strong");

        trackName.textContent =
            track.track_name;

        const artist =
            document.createElement("p");

        artist.textContent =
            track.artists;

        const genre =
            document.createElement("span");

        genre.className = "genre-label";
        genre.textContent =
            track.track_genre;

        trackCard.appendChild(trackName);
        trackCard.appendChild(artist);
        trackCard.appendChild(genre);

        trackList.appendChild(trackCard);
    }

    recentTracksContainer.appendChild(trackList);
}


contextSelect.addEventListener(
    "change",
    event => {
        displayRecentTracks(
            event.target.value
        );
    }
);


loadEvaluationContexts();