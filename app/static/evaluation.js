const contextSelect = document.getElementById("context-select");
const recentTracksContainer = document.getElementById("recent-tracks");
const statusMessage = document.getElementById("context-status");

const explorationInput =
    document.getElementById("exploration-level");

const explorationValue =
    document.getElementById("exploration-value");

const generateButton =
    document.getElementById("generate-button");

const recommendationStatus =
    document.getElementById("recommendation-status");

const recommendationResults =
    document.getElementById("recommendation-results");

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

function updateExplorationDisplay() {
    const value =
        Number(explorationInput.value);

    explorationValue.textContent =
        value.toFixed(2);
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

function getSelectedContext() {
    return evaluationContexts.find(
        context =>
            context.id === contextSelect.value
    );
}

async function generateRecommendations() {
    const context = getSelectedContext();

    if (!context) {
        recommendationStatus.textContent =
            "Please select a listening context.";

        return;
    }

    const explorationLevel =
        Number(explorationInput.value);

    const requestBody = {
        recent_tracks: context.recent_tracks.map(
            track => track.track_id
        ),
        exploration_level: explorationLevel,
        preferred_genres: [],
        preferred_artists: [],
        preference_strength: 0.0,
    };

    try {
        generateButton.disabled = true;
        generateButton.textContent =
            "Generating...";

        recommendationResults.innerHTML = "";

        recommendationStatus.textContent =
            "Generating recommendations...";

        const response = await fetch(
            "/recommend",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify(
                    requestBody
                ),
            }
        );

        if (!response.ok) {
            throw new Error(
                `Recommendation request failed: ${response.status}`
            );
        }

        const data = await response.json();

        displayRecommendations(data);

        recommendationStatus.textContent =
            "Recommendations generated successfully.";
    } catch (error) {
        console.error(error);

        recommendationStatus.textContent =
            "Unable to generate recommendations.";

        recommendationResults.innerHTML = `
            <p class="error-text">
                An error occurred while generating
                recommendations. Please try again.
            </p>
        `;
    } finally {
        generateButton.disabled =
            !contextSelect.value;

        generateButton.textContent =
            "Generate Recommendations";
    }
}

function displayRecommendations(data) {
    recommendationResults.innerHTML = "";

    const recommendations =
        Array.isArray(data)
            ? data
            : data.recommendations || [];

    if (recommendations.length === 0) {
        recommendationResults.innerHTML = `
            <p class="helper-text">
                No recommendations were returned.
            </p>
        `;

        return;
    }

    const visibleRecommendations =
        recommendations.slice(0, 5);

    const list =
        document.createElement("div");

    list.className = "recommendation-list";

    visibleRecommendations.forEach(
        (track, index) => {
            const card =
                document.createElement("article");

            card.className =
                "recommendation-card";

            const number =
                document.createElement("span");

            number.className =
                "recommendation-number";

            number.textContent =
                String(index + 1);

            const content =
                document.createElement("div");

            content.className =
                "recommendation-content";

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

            genre.className =
                "genre-label";

            genre.textContent =
                track.track_genre;

            content.appendChild(trackName);
            content.appendChild(artist);
            content.appendChild(genre);

            card.appendChild(number);
            card.appendChild(content);

            list.appendChild(card);
        }
    );

    recommendationResults.appendChild(list);
}

contextSelect.addEventListener(
    "change",
    event => {
        const contextId =
            event.target.value;

        displayRecentTracks(contextId);

        generateButton.disabled =
            !contextId;

        recommendationResults.innerHTML = "";

        recommendationStatus.textContent =
            contextId
                ? "Ready to generate recommendations."
                : "Select a listening context and generate recommendations.";
    }
);

explorationInput.addEventListener(
    "input",
    updateExplorationDisplay
);


loadEvaluationContexts();
updateExplorationDisplay();

generateButton.addEventListener(
    "click",
    generateRecommendations
);