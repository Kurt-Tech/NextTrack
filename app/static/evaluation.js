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

const preferredGenreSelect =
    document.getElementById("preferred-genre");

const preferenceStrengthInput =
    document.getElementById("preference-strength");

const preferenceStrengthValue =
    document.getElementById("preference-strength-value");

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

        const spotifyLink =
            document.createElement("a");

        spotifyLink.className =
            "spotify-link";

        spotifyLink.href =
            `https://open.spotify.com/track/${encodeURIComponent(track.track_id)}`;

        spotifyLink.target = "_blank";

        spotifyLink.rel =
            "noopener noreferrer";

        spotifyLink.textContent =
            "Listen on Spotify";

        const details =
            document.createElement("div");

        details.className = "recommendation-details";

        details.appendChild(genre);
        details.appendChild(spotifyLink);

        trackCard.appendChild(trackName);
        trackCard.appendChild(artist);
        trackCard.appendChild(details);

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

    const selectedGenre =
        preferredGenreSelect.value;

    const preferenceStrength =
        selectedGenre
            ? Number(
                preferenceStrengthInput.value
            )
            : 0.0;

    const requestBody = {
        recent_tracks: context.recent_tracks.map(
            track => track.track_id
        ),
        exploration_level: explorationLevel,
        preferred_genres:
            selectedGenre
                ? [selectedGenre]
                : [],
        preferred_artists: [],
        preference_strength:
            preferenceStrength,
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

            const details =
                document.createElement("div");

            details.className =
                "recommendation-details";

            const genre =
                document.createElement("span");

            genre.className =
                "genre-label";

            genre.textContent =
                track.track_genre;

            const spotifyLink =
                document.createElement("a");

            spotifyLink.className =
                "spotify-link";

            spotifyLink.href =
                `https://open.spotify.com/track/${encodeURIComponent(track.track_id)}`;

            spotifyLink.target = "_blank";

            spotifyLink.rel =
                "noopener noreferrer";

            spotifyLink.textContent =
                "Listen on Spotify";

            details.appendChild(genre);
            details.appendChild(spotifyLink);

            content.appendChild(trackName);
            content.appendChild(artist);
            content.appendChild(details);

            card.appendChild(number);
            card.appendChild(content);

            list.appendChild(card);
        }
    );

    recommendationResults.appendChild(list);
}

async function loadGenres() {
    try {
        const response =
            await fetch("/evaluation/genres");

        if (!response.ok) {
            throw new Error(
                `Failed to load genres: ${response.status}`
            );
        }

        const data =
            await response.json();

        populateGenreSelect(data.genres);
    } catch (error) {
        console.error(error);

        preferredGenreSelect.innerHTML = `
            <option value="">
                Unable to load genres
            </option>
        `;
    }
}

function populateGenreSelect(genres) {
    preferredGenreSelect.innerHTML = "";

    const noPreferenceOption =
        document.createElement("option");

    noPreferenceOption.value = "";
    noPreferenceOption.textContent =
        "No genre preference";

    preferredGenreSelect.appendChild(
        noPreferenceOption
    );

    for (const genre of genres) {
        const option =
            document.createElement("option");

        option.value = genre;
        option.textContent =
            formatGenreName(genre);

        preferredGenreSelect.appendChild(
            option
        );
    }

    preferredGenreSelect.disabled = false;
}

function formatGenreName(genre) {
    return genre
        .split("-")
        .map(
            word =>
                word.charAt(0).toUpperCase()
                + word.slice(1)
        )
        .join("-");
}

function updatePreferenceControls() {
    const hasPreference =
        Boolean(preferredGenreSelect.value);

    preferenceStrengthInput.disabled =
        !hasPreference;

    if (!hasPreference) {
        preferenceStrengthValue.textContent =
            "Inactive";

        return;
    }

    const value =
        Number(preferenceStrengthInput.value);

    preferenceStrengthValue.textContent =
        value.toFixed(2);
}

preferredGenreSelect.addEventListener(
    "change",
    updatePreferenceControls
);

preferenceStrengthInput.addEventListener(
    "input",
    updatePreferenceControls
);

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
loadGenres();

updateExplorationDisplay();
updatePreferenceControls();

generateButton.addEventListener(
    "click",
    generateRecommendations
);