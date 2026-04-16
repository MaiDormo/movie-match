const CACHE_CONFIG = {
    MOVIE_DETAILS_CACHE_KEY: 'movieDetailsCache',
    CACHE_DURATION: 30 * 60 * 1000
};

const cacheUtils = {
    set(movieId, data) {
        const cacheEntry = {
            timestamp: Date.now(),
            data: data
        };
        localStorage.setItem(`${CACHE_CONFIG.MOVIE_DETAILS_CACHE_KEY}_${movieId}`, JSON.stringify(cacheEntry));
    },

    get(movieId) {
        const cached = localStorage.getItem(`${CACHE_CONFIG.MOVIE_DETAILS_CACHE_KEY}_${movieId}`);
        if (!cached) return null;

        const cacheEntry = JSON.parse(cached);
        if (Date.now() - cacheEntry.timestamp > CACHE_CONFIG.CACHE_DURATION) {
            localStorage.removeItem(`${CACHE_CONFIG.MOVIE_DETAILS_CACHE_KEY}_${movieId}`);
            return null;
        }
        return cacheEntry.data;
    }
};

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
        // Check cache first
        const cachedDetails = cacheUtils.get(movieId);
        if (cachedDetails) {
            renderMovieDetails(cachedDetails);
            return;
        }

        // Fetch from API
        const response = await fetch(`http://localhost:5005/api/v1/movie_details?id=${movieId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch movie details');
        }

        if (data.status === 'error' || !data.data?.movie_details) {
            throw new Error(data.message || 'Movie not found');
        }

        const movieDetails = data.data.movie_details;

        // Cache the results
        cacheUtils.set(movieId, movieDetails);

        // Render
        renderMovieDetails(movieDetails);

    } catch (error) {
        console.error('Error fetching movie details:', error);
        showError(`Failed to load movie details: ${error.message}`);
    }
}

function renderMovieDetails(movieDetails) {
    // Update Hero Background
    if (movieDetails.omdb?.Poster && movieDetails.omdb.Poster !== 'N/A') {
        const hero = document.getElementById('hero');
        hero.style.setProperty('--hero-bg', `url(${movieDetails.omdb.Poster})`);
    }

    // Movie Info
    updateMovieInfo(movieDetails.omdb);
    
    // YouTube Video
    if (movieDetails.youtube?.embed_url) {
        const iframe = document.getElementById('youtube-frame');
        iframe.src = movieDetails.youtube.embed_url;
    } else {
        document.getElementById('video-section').style.display = 'none';
    }

    // Trivia
    if (movieDetails.trivia?.question) {
        updateTrivia(movieDetails.trivia);
    } else {
        document.querySelector('.trivia-card').style.display = 'none';
    }

    // Spotify
    if (movieDetails.spotify?.spotify_url) {
        updateSpotify(movieDetails.spotify);
    } else {
        document.getElementById('spotify-card').style.display = 'none';
    }

    // Streaming
    if (movieDetails.streaming?.services?.length > 0) {
        updateStreaming(movieDetails.streaming.services);
    } else {
        updateStreaming([]);
    }
}

function updateMovieInfo(movie) {
    const elements = {
        title: document.getElementById('title'),
        year: document.getElementById('year'),
        rating: document.getElementById('rating'),
        runtime: document.getElementById('runtime'),
        type: document.getElementById('type'),
        director: document.getElementById('director'),
        poster: document.getElementById('poster'),
        genres: document.getElementById('genres')
    };

    elements.title.textContent = movie.Title || 'N/A';
    elements.year.textContent = movie.Year || 'N/A';
    
    if (movie.imdbRating && movie.imdbRating !== 'N/A') {
        elements.rating.textContent = `★ ${movie.imdbRating}`;
    } else {
        elements.rating.style.display = 'none';
    }

    elements.runtime.textContent = movie.Runtime || '-- min';
    elements.type.textContent = movie.Type || 'Movie';
    
    elements.director.querySelector('span').textContent = movie.Director || 'N/A';
    
    // Poster
    const posterUrl = movie.Poster && movie.Poster !== 'N/A' 
        ? movie.Poster 
        : '/static/images/no-poster.jpg';
    elements.poster.src = posterUrl;
    elements.poster.alt = `${movie.Title} Poster`;

    // Genres
    if (movie.Genre && movie.Genre !== 'N/A') {
        const genres = movie.Genre.split(',').map(g => g.trim());
        elements.genres.innerHTML = genres.map(genre => 
            `<span class="genre-tag">${genre}</span>`
        ).join('');
    }
}

function updateTrivia(trivia) {
    const questionEl = document.getElementById('trivia-question');
    const optionsEl = document.getElementById('trivia-options');
    const feedbackEl = document.getElementById('trivia-feedback');

    questionEl.textContent = trivia.question;
    
    // Map options array
    const options = trivia.options || [];
    const buttons = optionsEl.querySelectorAll('.trivia-button');
    
    // Reset buttons
    buttons.forEach((btn, index) => {
        btn.disabled = false;
        btn.classList.remove('correct', 'wrong');
        btn.textContent = options[index] || `Option ${index + 1}`;
        btn.onclick = () => checkAnswer(index);
    });

    // Store correct answer index
    const correctAnswer = trivia.correct_answer;
    // Find which option matches the correct answer
    const correctIndex = options.findIndex(opt => 
        opt.toLowerCase() === correctAnswer.toLowerCase()
    );
    window.correctAnswerIndex = correctIndex >= 0 ? correctIndex : 0;
    
    feedbackEl.textContent = '';
    feedbackEl.className = 'trivia-feedback';
}

function checkAnswer(selectedIndex) {
    const buttons = document.querySelectorAll('.trivia-button');
    const feedbackEl = document.getElementById('trivia-feedback');

    buttons.forEach(btn => btn.disabled = true);

    if (selectedIndex === window.correctAnswerIndex) {
        buttons[selectedIndex].classList.add('correct');
        feedbackEl.textContent = '🎉 Correct! Well done!';
        feedbackEl.className = 'trivia-feedback correct';
    } else {
        buttons[selectedIndex].classList.add('wrong');
        buttons[window.correctAnswerIndex].classList.add('correct');
        feedbackEl.textContent = `❌ Wrong! The correct answer was: ${buttons[window.correctAnswerIndex].textContent}`;
        feedbackEl.className = 'trivia-feedback wrong';
    }
}

function updateSpotify(spotify) {
    document.getElementById('spotify-cover').src = spotify.cover_url || 'https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_White.png';
    document.getElementById('spotify-title').textContent = spotify.name || 'Movie Soundtrack';
    document.getElementById('spotify-subtitle').textContent = 'Listen on Spotify';
    
    window.spotifyUrl = spotify.spotify_url;
}

function openSpotify() {
    if (window.spotifyUrl) {
        window.open(window.spotifyUrl, '_blank');
    }
}

function updateStreaming(services) {
    const container = document.getElementById('streaming-content');
    
    if (!services || services.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 3H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5v2h8v-2h5c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 14H3V5h18v12z"/>
                </svg>
                <p>No streaming services available</p>
            </div>
        `;
        return;
    }

    container.innerHTML = services.map(service => {
        const typeClass = getStreamingTypeClass(service.service_type);
        return `
            <a href="${service.link}" target="_blank" class="streaming-item">
                <img class="streaming-logo" src="${service.logo || ''}" alt="${service.service_name}" 
                     onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23333%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23fff%22 font-size=%2230%22>▶</text></svg>'">
                <span class="streaming-name">${service.service_name}</span>
                <span class="streaming-type ${typeClass}">${service.service_type}</span>
            </a>
        `;
    }).join('');
}

function getStreamingTypeClass(type) {
    if (!type) return '';
    const t = type.toLowerCase();
    if (t.includes('subscription') || t.includes('stream')) return 'subscribe';
    if (t.includes('buy')) return 'buy';
    if (t.includes('rent')) return 'rent';
    return '';
}

function showError(message) {
    // Hide main content
    document.querySelector('.hero').style.display = 'none';
    document.querySelector('.main-content').style.display = 'none';
    
    // Show error
    const errorContainer = document.getElementById('error-container');
    document.getElementById('error-message').textContent = message;
    errorContainer.style.display = 'flex';
}

// Initialize with skeleton-like loading state
document.getElementById('title').classList.add('skeleton', 'skeleton-text-lg');
document.getElementById('year').classList.add('skeleton', 'skeleton-text-sm');