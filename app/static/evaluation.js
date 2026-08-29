const recentTracksContainer = document.getElementById("recent-tracks");

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

const exploreModeButton =
    document.getElementById("explore-mode-button");

const studyModeButton =
    document.getElementById("study-mode-button");

const exploreMode =
    document.getElementById("explore-mode");

const studyMode =
    document.getElementById("study-mode");

const participantCodeInput =
    document.getElementById("participant-code");

const studyContextSelect =
    document.getElementById("study-context-select");

const studyRecentTracks =
    document.getElementById("study-recent-tracks");

const generateStudyButton =
    document.getElementById("generate-study-button");

const studyStatus =
    document.getElementById("study-status");

const studyResultsSection =
    document.getElementById("study-results-section");

const studySetA =
    document.getElementById("study-set-a");

const studySetB =
    document.getElementById("study-set-b");

const trackSearchInput =
    document.getElementById("track-search");

const trackSearchButton =
    document.getElementById("track-search-button");

const trackSearchStatus =
    document.getElementById("track-search-status");

const trackSearchResults =
    document.getElementById("track-search-results");

const selectedTrackCount =
    document.getElementById("selected-track-count");

let evaluationContexts = [];

const MAX_RECENT_TRACKS = 3;

let selectedRecentTracks = [];
let lastSearchResults = [];

const STUDY_CONTEXT_IDS = [
    "rock",
    "hip-hop",
    "country",
];

async function loadEvaluationContexts() {
    try {
        const response =
            await fetch("/evaluation/contexts");

        if (!response.ok) {
            throw new Error(
                `Failed to load contexts: ${response.status}`
            );
        }

        const data =
            await response.json();

        evaluationContexts =
            data.contexts;

        populateStudyContextSelect();
    } catch (error) {
        console.error(error);

        studyStatus.textContent =
            "Unable to load study contexts.";
    }
}

function updateExplorationDisplay() {
    const value =
        Number(explorationInput.value);

    explorationValue.textContent =
        value.toFixed(2);
}

function renderSelectedRecentTracks() {
    recentTracksContainer.innerHTML = "";

    selectedTrackCount.textContent =
        `${selectedRecentTracks.length} of ${MAX_RECENT_TRACKS} selected`;

    if (selectedRecentTracks.length === 0) {
        recentTracksContainer.innerHTML = `
            <p class="helper-text">
                Choose a preset or search for three tracks.
            </p>
        `;

        updateExploreControls();
        return;
    }

    const trackList =
        document.createElement("div");

    trackList.className = "track-list";

    for (const track of selectedRecentTracks) {
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

        const details =
            document.createElement("div");

        details.className =
            "recommendation-details";

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

        const removeButton =
            document.createElement("button");

        removeButton.type = "button";

        removeButton.className =
            "remove-track-button";

        removeButton.textContent =
            "Remove";

        removeButton.addEventListener(
            "click",
            () => {
                removeRecentTrack(
                    track.track_id
                );
            }
        );

        details.appendChild(genre);
        details.appendChild(spotifyLink);
        details.appendChild(removeButton);

        trackCard.appendChild(trackName);
        trackCard.appendChild(artist);
        trackCard.appendChild(details);

        trackList.appendChild(trackCard);
    }

    recentTracksContainer.appendChild(
        trackList
    );

    updateExploreControls();
}


async function generateRecommendations() {
    if (
        selectedRecentTracks.length !==
        MAX_RECENT_TRACKS
    ) {
        recommendationStatus.textContent =
            "Select exactly three recent tracks.";

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
        recent_tracks:
            selectedRecentTracks.map(
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
            selectedRecentTracks.length !==
            MAX_RECENT_TRACKS;

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

function setInterfaceMode(mode) {
    const isExplore =
        mode === "explore";

    exploreMode.hidden =
        !isExplore;

    studyMode.hidden =
        isExplore;

    exploreModeButton.classList.toggle(
        "active",
        isExplore
    );

    studyModeButton.classList.toggle(
        "active",
        !isExplore
    );

    exploreModeButton.setAttribute(
        "aria-pressed",
        String(isExplore)
    );

    studyModeButton.setAttribute(
        "aria-pressed",
        String(!isExplore)
    );
}

function populateStudyContextSelect() {
    studyContextSelect.innerHTML = "";

    const placeholder =
        document.createElement("option");

    placeholder.value = "";
    placeholder.textContent =
        "Select a study context";

    studyContextSelect.appendChild(
        placeholder
    );

    for (const contextId of STUDY_CONTEXT_IDS) {
        const context =
            evaluationContexts.find(
                item =>
                    item.id === contextId
            );

        if (!context) {
            continue;
        }

        const option =
            document.createElement("option");

        option.value =
            context.id;

        option.textContent =
            context.name;

        studyContextSelect.appendChild(
            option
        );
    }

    studyContextSelect.disabled = false;
}

function displayStudyRecentTracks(contextId) {
    studyRecentTracks.innerHTML = "";

    const context =
        evaluationContexts.find(
            item =>
                item.id === contextId
        );

    if (!context) {
        studyRecentTracks.innerHTML = `
            <p class="helper-text">
                Select a listening context to continue.
            </p>
        `;

        return;
    }

    const heading =
        document.createElement("h3");

    heading.textContent =
        `${context.name} Recent Tracks`;

    studyRecentTracks.appendChild(
        heading
    );

    const trackList =
        document.createElement("div");

    trackList.className =
        "track-list";

    for (const track of context.recent_tracks) {
        const card =
            document.createElement("article");

        card.className =
            "track-card";

        const trackName =
            document.createElement("strong");

        trackName.textContent =
            track.track_name;

        const artist =
            document.createElement("p");

        artist.textContent =
            track.artists;

        const spotifyLink =
            document.createElement("a");

        spotifyLink.className =
            "spotify-link";

        spotifyLink.href =
            `https://open.spotify.com/track/${encodeURIComponent(track.track_id)}`;

        spotifyLink.target =
            "_blank";

        spotifyLink.rel =
            "noopener noreferrer";

        spotifyLink.textContent =
            "Listen on Spotify";

        card.appendChild(trackName);
        card.appendChild(artist);
        card.appendChild(spotifyLink);

        trackList.appendChild(card);
    }

    studyRecentTracks.appendChild(
        trackList
    );
}

function getParticipantNumber() {
    const value =
        participantCodeInput.value.trim();

    const match =
        value.match(/^P?(\d+)$/i);

    if (!match) {
        return null;
    }

    return Number(match[1]);
}

function getStudyConditions(participantNumber) {
    const lowExploration = 0.0;
    const highExploration = 1.0;

    const isOdd =
        participantNumber % 2 === 1;

    if (isOdd) {
        return {
            setA: lowExploration,
            setB: highExploration,
        };
    }

    return {
        setA: highExploration,
        setB: lowExploration,
    };
}

function updateStudyControls() {
    const participantNumber =
        getParticipantNumber();

    const hasContext =
        Boolean(studyContextSelect.value);

    generateStudyButton.disabled =
        participantNumber === null
        || !hasContext;

    if (participantNumber === null) {
        studyStatus.textContent =
            "Enter a valid participant code such as P01.";

        return;
    }

    if (!hasContext) {
        studyStatus.textContent =
            "Select a listening context.";
        return;
    }

    studyStatus.textContent =
        "Ready to generate the comparison.";
}

async function requestStudyRecommendations(
    context,
    explorationLevel
) {
    const requestBody = {
        recent_tracks:
            context.recent_tracks.map(
                track => track.track_id
            ),

        exploration_level:
            explorationLevel,

        preferred_genres: [],

        preferred_artists: [],

        preference_strength: 0.0,
    };

    const response =
        await fetch(
            "/recommend",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body:
                    JSON.stringify(
                        requestBody
                    ),
            }
        );

    if (!response.ok) {
        throw new Error(
            `Study recommendation request failed: ${response.status}`
        );
    }

    return response.json();
}

function displayStudyRecommendations(
    container,
    data
) {
    container.innerHTML = "";

    const recommendations =
        Array.isArray(data)
            ? data
            : data.recommendations || [];

    const visibleRecommendations =
        recommendations.slice(0, 5);

    if (visibleRecommendations.length === 0) {
        container.innerHTML = `
            <p class="helper-text">
                No recommendations were returned.
            </p>
        `;

        return;
    }

    visibleRecommendations.forEach(
        (track, index) => {
            const card =
                document.createElement("article");

            card.className =
                "study-track-card";

            const name =
                document.createElement("strong");

            name.textContent =
                `${index + 1}. ${track.track_name}`;

            const artist =
                document.createElement("p");

            artist.textContent =
                track.artists;

            const spotifyLink =
                document.createElement("a");

            spotifyLink.className =
                "spotify-link";

            spotifyLink.href =
                `https://open.spotify.com/track/${encodeURIComponent(track.track_id)}`;

            spotifyLink.target =
                "_blank";

            spotifyLink.rel =
                "noopener noreferrer";

            spotifyLink.textContent =
                "Listen on Spotify";

            card.appendChild(name);
            card.appendChild(artist);
            card.appendChild(spotifyLink);

            container.appendChild(card);
        }
    );
}

async function generateStudyComparison() {
    const participantNumber =
        getParticipantNumber();

    if (participantNumber === null) {
        studyStatus.textContent =
            "Enter a valid participant code.";

        return;
    }

    const context =
        evaluationContexts.find(
            item =>
                item.id ===
                studyContextSelect.value
        );

    if (!context) {
        studyStatus.textContent =
            "Select a listening context.";

        return;
    }

    const conditions =
        getStudyConditions(
            participantNumber
        );

    try {
        generateStudyButton.disabled =
            true;

        generateStudyButton.textContent =
            "Generating...";

        studyStatus.textContent =
            "Generating comparison...";

        studyResultsSection.hidden =
            true;

        studySetA.innerHTML = "";
        studySetB.innerHTML = "";

        const [
            setAData,
            setBData,
        ] = await Promise.all([
            requestStudyRecommendations(
                context,
                conditions.setA
            ),

            requestStudyRecommendations(
                context,
                conditions.setB
            ),
        ]);

        displayStudyRecommendations(
            studySetA,
            setAData
        );

        displayStudyRecommendations(
            studySetB,
            setBData
        );

        studyResultsSection.hidden =
            false;

        studyStatus.textContent =
            "Comparison generated successfully.";
    } catch (error) {
        console.error(error);

        studyStatus.textContent =
            "Unable to generate the study comparison.";
    } finally {
        generateStudyButton.textContent =
            "Generate Comparison";

        updateStudyControls();
    }
}

function updateExploreControls() {
    const hasThreeTracks =
        selectedRecentTracks.length ===
        MAX_RECENT_TRACKS;

    generateButton.disabled =
        !hasThreeTracks;

    if (!hasThreeTracks) {
        const remaining =
            MAX_RECENT_TRACKS -
            selectedRecentTracks.length;

        recommendationStatus.textContent =
            `Select ${remaining} more recent ${remaining === 1
                ? "track"
                : "tracks"
            } to generate recommendations.`;
    }
}

function addRecentTrack(track) {
    const alreadySelected =
        selectedRecentTracks.some(
            item =>
                item.track_id ===
                track.track_id
        );

    if (
        alreadySelected
        || selectedRecentTracks.length >=
        MAX_RECENT_TRACKS
    ) {
        return;
    }

    selectedRecentTracks.push(track);

    renderSelectedRecentTracks();
    renderSearchResults(lastSearchResults);
}

function removeRecentTrack(trackId) {
    selectedRecentTracks =
        selectedRecentTracks.filter(
            track =>
                track.track_id !== trackId
        );

    recommendationResults.innerHTML = "";

    renderSelectedRecentTracks();
    renderSearchResults(lastSearchResults);
}

async function searchExploreTracks() {
    const query =
        trackSearchInput.value.trim();

    if (query.length < 2) {
        trackSearchStatus.textContent =
            "Enter at least two characters to search.";

        trackSearchResults.innerHTML = "";
        return;
    }

    try {
        trackSearchButton.disabled = true;

        trackSearchButton.textContent =
            "Searching...";

        trackSearchStatus.textContent =
            "Searching the catalogue...";

        const response = await fetch(
            `/evaluation/search?query=${encodeURIComponent(query)}`
        );

        if (!response.ok) {
            throw new Error(
                `Track search failed: ${response.status}`
            );
        }

        const data =
            await response.json();

        lastSearchResults =
            data.results;

        renderSearchResults(
            lastSearchResults
        );

        trackSearchStatus.textContent =
            data.results.length > 0
                ? `${data.results.length} results found.`
                : "No matching tracks found.";
    } catch (error) {
        console.error(error);

        lastSearchResults = [];

        trackSearchResults.innerHTML = "";

        trackSearchStatus.textContent =
            "Unable to search tracks.";
    } finally {
        trackSearchButton.disabled = false;

        trackSearchButton.textContent =
            "Search";
    }
}

function renderSearchResults(results) {
    trackSearchResults.innerHTML = "";

    if (results.length === 0) {
        return;
    }

    const resultList =
        document.createElement("div");

    resultList.className =
        "search-result-list";

    for (const track of results) {
        const card =
            document.createElement("article");

        card.className =
            "search-result-card";

        const content =
            document.createElement("div");

        content.className =
            "search-result-content";

        const name =
            document.createElement("strong");

        name.textContent =
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

        const actions =
            document.createElement("div");

        actions.className =
            "search-result-actions";

        const spotifyLink =
            document.createElement("a");

        spotifyLink.className =
            "spotify-link";

        spotifyLink.href =
            `https://open.spotify.com/track/${encodeURIComponent(track.track_id)}`;

        spotifyLink.target =
            "_blank";

        spotifyLink.rel =
            "noopener noreferrer";

        spotifyLink.textContent =
            "Listen";

        const addButton =
            document.createElement("button");

        addButton.type =
            "button";

        addButton.className =
            "add-track-button";

        const alreadySelected =
            selectedRecentTracks.some(
                item =>
                    item.track_id ===
                    track.track_id
            );

        const selectionFull =
            selectedRecentTracks.length >=
            MAX_RECENT_TRACKS;

        if (alreadySelected) {
            addButton.textContent =
                "Selected";

            addButton.disabled = true;
        } else if (selectionFull) {
            addButton.textContent =
                "3 tracks selected";

            addButton.disabled = true;
        } else {
            addButton.textContent =
                "Add";

            addButton.addEventListener(
                "click",
                () => addRecentTrack(track)
            );
        }

        content.appendChild(name);
        content.appendChild(artist);
        content.appendChild(genre);

        actions.appendChild(
            spotifyLink
        );

        actions.appendChild(
            addButton
        );

        card.appendChild(content);
        card.appendChild(actions);

        resultList.appendChild(card);
    }

    trackSearchResults.appendChild(
        resultList
    );
}

setInterfaceMode("explore");
updateStudyControls();

explorationInput.addEventListener(
    "input",
    updateExplorationDisplay
);


loadEvaluationContexts();
loadGenres();

updateExplorationDisplay();
updatePreferenceControls();
renderSelectedRecentTracks();

generateButton.addEventListener(
    "click",
    generateRecommendations
);

exploreModeButton.addEventListener(
    "click",
    () => setInterfaceMode("explore")
);

studyModeButton.addEventListener(
    "click",
    () => setInterfaceMode("study")
);

participantCodeInput.addEventListener(
    "input",
    updateStudyControls
);

studyContextSelect.addEventListener(
    "change",
    event => {
        displayStudyRecentTracks(
            event.target.value
        );

        studyResultsSection.hidden =
            true;

        studySetA.innerHTML = "";
        studySetB.innerHTML = "";

        updateStudyControls();
    }
);

generateStudyButton.addEventListener(
    "click",
    generateStudyComparison
);

trackSearchButton.addEventListener(
    "click",
    searchExploreTracks
);

trackSearchInput.addEventListener(
    "keydown",
    event => {
        if (event.key === "Enter") {
            event.preventDefault();
            searchExploreTracks();
        }
    }
);