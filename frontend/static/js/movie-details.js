document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('id');

    if (!movieId) {
        showError('No movie ID provided. Please provide a valid IMDB movie ID.');
        return;
    }

    fetchMovieDetails(movieId);
});

async function fetchMovieDetails(movieId) {
    try {
        const response = await fetch(`http://localhost:5005/api/v1/movie_details?movie_id=${movieId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch movie details');
        }

        if (data.status === 'fail') {
            throw new Error(data.message || 'Movie not found');
        }

        // Update movie details
        updateMovieInfo(data.data.movie_details.omdb);

        // Update additional content
        updateYouTubeTrailer(data.data.movie_details.youtube);
        updateSpotifyPlaylist(data.data.movie_details.spotify);
        updateStreamingAvailability(data.data.movie_details.streaming);
        updateTrivia(data.data.movie_details.trivia);

    } catch (error) {
        console.error('Error fetching movie details:', error);
        showError(`Failed to load movie details: ${error.message}`);
    }
}

function updateMovieInfo(movie) {
    const elements = {
        title: document.getElementById("title"),
        year: document.getElementById("year"),
        director: document.getElementById("director"),
        poster: document.getElementById("poster")
    };

    // Check if all required elements exist
    if (!elements.title || !elements.year || !elements.director || !elements.poster) {
        throw new Error('Required movie detail elements not found in the DOM');
    }

    // Update text content with fallbacks
    elements.title.textContent = `${movie.Title || 'N/A'}`;
    elements.year.textContent = `Year: ${movie.Year || 'N/A'}`;
    elements.director.textContent = `Director(s): ${movie.Director || 'N/A'}`;

    // Update poster
    const posterUrl = movie.Poster !== 'N/A' ? movie.Poster : '/static/images/no-poster.jpg';
    elements.poster.src = posterUrl;
    elements.poster.alt = `${movie.Title} Poster`;

    // Update background if possible
    try {
        updateBackground(posterUrl);
    } catch (error) {
        console.warn('Failed to update background:', error);
    }
}

function updateYouTubeTrailer(youtubeData) {
    const iframe = document.querySelector(".video-container iframe");
    iframe.src = youtubeData.data.embed_url;
}

function updateSpotifyPlaylist(spotifyData) {
    const spotifyContainer = document.getElementById("spotify-container");
    document.getElementById("spotify-cover").src = spotifyData.data.cover_url;
    document.getElementById("playlist-title").textContent = spotifyData.data.name;
    spotifyContainer.dataset.link = spotifyData.data.spotify_url;
}

function updateStreamingAvailability(streamingData) {
    const streamingDescription = document.getElementById('streaming-description');
    
    // Handle null/undefined streaming data
    if (!streamingData || !streamingData.data || streamingData.data.length === 0) {
        streamingDescription.innerHTML = `
            <div class="no-streaming-message" style="text-align: center; padding: 20px;">
                <p>No streaming services available for this movie</p>
            </div>
        `;
        return;
    }

    // If we have data, display the streaming services
    const availabilityList = streamingData.data.map(item => {
        return `
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <img src="${item.logo || ''}" alt="${item.service_name}" style="width: 100px; height: 100px; margin-right: 30px; margin-left: 20px;">
                <a href="${item.link}" target="_blank" style="text-decoration: none;">
                    <button class="streaming-button">
                        ${item.service_type}
                    </button>
                </a>
            </div>
        `;
    }).join('');

    streamingDescription.innerHTML = availabilityList;
}

function updateTrivia(triviaData) {
    const questionElement = document.getElementById("question");
    const formattedQuestion = triviaData.ai_question.replace(/\n/g, "<br>");
    questionElement.innerHTML = formattedQuestion;
    window.correctAnswer = triviaData.ai_answer;
}

function showError(message) {
    const container = document.querySelector('.container');
    if (!container) {
        console.error('Error container not found');
        return;
    }

    container.innerHTML = `
        <div class="error-message">
            <h2>Error</h2>
            <p>${message}</p>
            <button onclick="window.history.back()" class="back-button">Go Back</button>
        </div>
    `;
}

// Modifica sfondo in base ai colori del poster
function updateBackground(posterUrl) {
    const img = new Image();
    img.src = posterUrl + "?not-from-cache-please"; // Aggiungi il parametro per evitare la cache
    img.crossOrigin = "Anonymous";
    img.onload = function () {
        const colorThief = new ColorThief();
        try {
            const palette = colorThief.getPalette(img, 2); // Estrai i colori
            if (palette && palette.length >= 2) {
                const [color1, color2] = palette;
                document.body.style.background = `linear-gradient(135deg, rgb(${color1.join(',')}) , rgb(${color2.join(',')}))`;
                document.body.style.backgroundAttachment = 'fixed';
            }
        } catch (error) {
            console.error("Errore nell'estrazione dei colori:", error);
        }
    };
}

function checkAnswer(selected) {
    const feedback = document.getElementById("feedback");
    const buttons = document.querySelectorAll(".trivia-button");

    buttons.forEach(button => {
        button.disabled = true;
    });

    const selectedButton = buttons[selected - 1];
    selectedButton.style.backgroundColor = "#d35400";
    selectedButton.style.color = "white";

    if (String(selected) === window.correctAnswer) {
        feedback.textContent = "Risposta corretta!";
        feedback.style.color = "green";
    } else {
        feedback.textContent = `Risposta sbagliata. Quella corretta è: ${window.correctAnswer}`;
        feedback.style.color = "red";
    }
}

// Funzione per aprire il link della playlist
function openSpotify() {
    const spotifyContainer = document.getElementById("spotify-container");
    const link = spotifyContainer.dataset.link;
    if (link) {
        window.open(link, "_blank");
    } else {
        console.error("Link Spotify non disponibile");
    }
}