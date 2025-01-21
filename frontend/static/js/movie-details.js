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
        const response = await fetch(`http://localhost:5001/api/v1/find?id=${movieId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch movie details');
        }

        if (data.status === 'fail') {
            throw new Error(data.message || 'Movie not found');
        }

        // Update movie details
        updateMovieInfo(data);
        
        // Fetch additional content only if main content loaded successfully
        try {
            await Promise.all([
                data.Title && fetchYouTubeTrailer(data.Title),
                data.Title && fetchSpotifyPlaylist(data.Title),
                movieId && fetchStreamingAvailability(movieId),
                data.Title && fetchTrivia(data.Title)
            ].filter(Boolean));
        } catch (contentError) {
            console.error('Error loading additional content:', contentError);
            // Don't throw - allow partial content loading
        }

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
    elements.title.textContent = `Title: ${movie.Title || 'N/A'}`;
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

async function fetchTrivia(movieTitle) {
    const questionElement = document.getElementById("question");
    if (!questionElement) {
        console.warn('Trivia section not found');
        return;
    }

    try {
        const url = `http://localhost:5007/api/v1/get_trivia?movie_title=${encodeURIComponent(movieTitle)}`;
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch trivia');
        }

        if (data.status === "success") {
            const formattedQuestion = data.ai_question.replace(/\n/g, "<br>");
            questionElement.innerHTML = formattedQuestion;
            window.correctAnswer = data.ai_answer;
        } else {
            throw new Error(data.message || 'No trivia found');
        }

    } catch (error) {
        console.error("Error fetching trivia:", error);
        questionElement.innerHTML = "Sorry, we couldn't load a trivia question for this movie.";
        
        const triviaButtons = document.querySelectorAll('.trivia button');
        triviaButtons.forEach(button => {
            if (button) button.style.display = 'none';
        });
    }
}

function checkAnswer(selected) {
    const feedback = document.getElementById("feedback");
    const buttons = document.querySelectorAll(".trivia button");

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

async function fetchStreamingAvailability(movieId) {
    try {
        const url = `http://localhost:5002/api/v1/avail?imdb_id=${movieId}&country=it`;
        const response = await fetch(url);
        const responseData = await response.json();

        // Check if response is successful and has data
        if (responseData.status !== "success" || !responseData.data) {
            throw new Error(responseData.message || "No streaming data available");
        }

        // Convert data to array if it's not already
        const servicesArray = Array.isArray(responseData.data) ? 
            responseData.data : 
            [responseData.data];
        
        // Map through the services array
        const availabilityList = servicesArray.length > 0 ? servicesArray.map(item => {
            return `
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="${item.logo || ''}" alt="${item.service_name}" style="width: 100px; height: 100px; margin-right: 30px; margin-left: 20px;">
                    <a href="${item.link}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: orange; color: white; padding: 10px 20px; border-radius: 20px; cursor: pointer;">
                            ${item.service_type}
                        </div>
                    </a>
                </div>
            `;
        }).join('') : '';

        // Show no results message if list is empty
        if (!availabilityList) {
            document.getElementById('streaming-description').textContent = "No streaming services available.";
            return;
        }

        document.getElementById('streaming-description').innerHTML = availabilityList;
    } catch (error) {
        console.error("Error fetching streaming availability:", error);
        document.getElementById('streaming-description').textContent = 
            "Unable to retrieve streaming availability data.";
    }
}

async function fetchYouTubeTrailer(movieTitle) {
    try {
        const query = encodeURIComponent(`${movieTitle} trailer`);
        const url = `http://localhost:5009/api/v1/get_video?query=${query}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.embed_url) {
            const iframe = document.querySelector(".video-container iframe");
            iframe.src = data.embed_url;
        } else {
            console.error("Nessun video trovato per il trailer.");
        }
    } catch (error) {
        console.error("Errore durante il recupero del trailer:", error);
    }
}

async function fetchSpotifyPlaylist(movieTitle) {
    try {
        const url = `http://localhost:5004/api/v1/search_playlist?playlist_name=${encodeURIComponent(movieTitle)}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.spotify_url && data.cover_url && data.name) {
            // Aggiorna i dettagli del contenitore
            const spotifyContainer = document.getElementById("spotify-container");
            document.getElementById("spotify-cover").src = data.cover_url;
            document.getElementById("playlist-title").textContent = data.name;
            spotifyContainer.dataset.link = data.spotify_url;
        } else {
            console.error("Dati insufficienti per la playlist");
        }
    } catch (error) {
        console.error("Errore durante il recupero della playlist:", error);
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