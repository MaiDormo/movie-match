const CACHE_CONFIG = {
    MOVIES_CACHE_KEY: 'moviesCache',
    GENRES_CACHE_KEY: 'genresCache',
    CACHE_DURATION: 30 * 60 * 1000
};

const cacheUtils = {
    set(key, data) {
        const cacheEntry = {
            timestamp: Date.now(),
            data: data
        };
        localStorage.setItem(key, JSON.stringify(cacheEntry));
    },

    get(key) {
        const cached = localStorage.getItem(key);
        if (!cached) return null;

        const cacheEntry = JSON.parse(cached);
        if (Date.now() - cacheEntry.timestamp > CACHE_CONFIG.CACHE_DURATION) {
            localStorage.removeItem(key);
            return null;
        }
        return cacheEntry.data;
    },

    getCacheKey(type, query) {
        return `${type}_${query}`;
    }
};

function renderMovies(movieGridElement, movies, userGenres = []) {
    const existingSpinner = movieGridElement.querySelector('#loading-spinner');
    movieGridElement.innerHTML = '';

    if (existingSpinner) {
        movieGridElement.appendChild(existingSpinner);
    }

    if (!movies || movies.length === 0) {
        movieGridElement.innerHTML += `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
                </svg>
                <h3>No movies found</h3>
                <p>Try a different search term</p>
            </div>
        `;
        return;
    }

    movies.forEach(movie => {
        if (!movie) return;

        const movieCard = document.createElement('div');
        movieCard.classList.add('movie-card');

        const posterUrl = movie.Poster !== 'N/A' ? movie.Poster : '/static/images/no-poster.jpg';
        const rating = movie.imdbRating || movie.vote_average || 'N/A';
        const year = movie.Year || (movie.release_date ? movie.release_date.split('-')[0] : 'N/A');

        movieCard.innerHTML = `
            <img class="movie-poster" src="${posterUrl}" alt="${movie.Title || movie.title || 'Movie'}">
            <div class="movie-info">
                <h3 class="movie-title">${movie.Title || movie.title || 'Unknown'}</h3>
                <div class="movie-year">
                    <span>${year}</span>
                    ${rating !== 'N/A' ? `<span class="movie-rating">★ ${rating}</span>` : ''}
                </div>
            </div>
        `;

        movieCard.onclick = () => {
            window.location.href = `/movie?id=${movie.imdbID || movie.id}`;
        };

        movieGridElement.appendChild(movieCard);
    });
}

async function loadMovies(query = '') {
    const movieGrid = document.getElementById('movie-grid');
    const spinner = document.getElementById('loading-spinner');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    console.log('Elements:', { movieGrid: !!movieGrid, spinner: !!spinner, searchInput: !!searchInput, searchButton: !!searchButton });

    if (!movieGrid || !searchInput || !searchButton) {
        console.error('Required elements not found');
        return;
    }

    const searchQuery = query || searchInput.value;

    if (!searchQuery) {
        alert('Please enter a movie title!');
        return;
    }

    const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.MOVIES_CACHE_KEY, searchQuery);
    const cachedMovies = cacheUtils.get(cacheKey);

    if (cachedMovies) {
        renderMovies(movieGrid, cachedMovies);
        return;
    }

    if (spinner) spinner.style.display = 'flex';
    searchButton.disabled = true;

    try {
        const response = await fetch(`http://localhost:5017/api/v1/movies/search-by-text?query=${encodeURIComponent(searchQuery)}`);
        const data_json = await response.json();

        if (!response.ok || data_json.status === 'error') {
            throw new Error(data_json.message || 'Movies not found');
        }

        cacheUtils.set(cacheKey, data_json.data.movie_list);
        renderMovies(movieGrid, data_json.data.movie_list);
    } catch (error) {
        console.error('Error loading movies:', error);
        movieGrid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
                <h3>Error loading movies</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        spinner.style.display = 'none';
        searchButton.disabled = false;
    }
}

async function discoverMoviesByGenre() {
    const movieGrid = document.getElementById('movie-grid');
    const spinner = document.getElementById('loading-spinner');
    const searchButton = document.getElementById('search-button');

    spinner.style.display = 'flex';
    searchButton.disabled = true;

    try {
        const userGenres = await fetch(`http://localhost:5017/api/v1/user-genres?user_id=0b8ac00c-a52b-4649-bd75-699b49c00ce3`);
        const genresData = await userGenres.json();

        const preferredGenres = genresData.data.user_genres
            .filter(genre => genre.isPreferred)
            .map(genre => genre.genreId)
            .join(',');

        if (!preferredGenres) {
            alert('No preferred genres found! Select some genres first.');
            spinner.style.display = 'none';
            searchButton.disabled = false;
            return;
        }

        const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.MOVIES_CACHE_KEY, `genres_${preferredGenres}`);
        const cachedMovies = cacheUtils.get(cacheKey);

        if (cachedMovies) {
            renderMovies(movieGrid, cachedMovies, genresData.data.user_genres);
            spinner.style.display = 'none';
            searchButton.disabled = false;
            return;
        }

        const response = await fetch(`http://localhost:5017/api/v1/movies/search-by-genre?with_genres=${preferredGenres}`);
        const data = await response.json();

        spinner.style.display = 'none';
        searchButton.disabled = false;

        if (data.status === "success" && data.data.movie_list) {
            cacheUtils.set(cacheKey, data.data.movie_list);
            renderMovies(movieGrid, data.data.movie_list, genresData.data.user_genres);
        } else {
            renderMovies(movieGrid, []);
        }
    } catch (error) {
        console.error('Error discovering movies:', error);
        spinner.style.display = 'none';
        searchButton.disabled = false;
        renderMovies(movieGrid, []);
    }
}

async function createGenres(userId) {
    const genreTagsContainer = document.getElementById('genre-tags');

    const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.GENRES_CACHE_KEY, userId);
    const cachedGenres = cacheUtils.get(cacheKey);

    if (cachedGenres) {
        renderGenreTags(genreTagsContainer, cachedGenres, userId);
        return;
    }

    try {
        const response = await fetch(`http://localhost:5017/api/v1/user-genres?user_id=${userId}`);
        const data = await response.json();

        if (!response.ok || data.status === 'error') {
            throw new Error(data.message || 'Failed to fetch user genres');
        }

        const userGenres = data.data.user_genres;
        cacheUtils.set(cacheKey, userGenres);
        renderGenreTags(genreTagsContainer, userGenres, userId);
    } catch (error) {
        console.error('Error creating genre tags:', error);
    }
}

function renderGenreTags(container, genres, userId) {
    container.innerHTML = '';

    genres.forEach(genre => {
        const tag = document.createElement('div');
        tag.classList.add('genre-tag');
        tag.textContent = genre.name;

        if (genre.isPreferred) {
            tag.classList.add('selected');
        }

        tag.onclick = () => {
            tag.classList.toggle('selected');
        };

        container.appendChild(tag);
    });

    setupConfirmButton(genres, userId);
}

function setupConfirmButton(genres, userId) {
    const confirmButton = document.getElementById('confirm-button');
    if (!confirmButton) return;

    confirmButton.onclick = () => {
        const selectedGenres = Array.from(document.querySelectorAll('.genre-tag.selected'))
            .map(tag => {
                const genre = genres.find(g => g.name === tag.textContent);
                return genre ? genre.genreId : null;
            })
            .filter(genreId => genreId !== null);

        if (selectedGenres.length > 0) {
            updateUserPreferences(userId, selectedGenres);
            const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.GENRES_CACHE_KEY, userId);
            const updatedGenres = genres.map(g => ({
                ...g,
                isPreferred: selectedGenres.includes(g.genreId)
            }));
            cacheUtils.set(cacheKey, updatedGenres);
        } else {
            alert('No genres selected!');
        }
    };
}

async function updateUserPreferences(userId, preferences) {
    try {
        const response = await fetch(`http://localhost:5017/api/v1/user-genres/update?user_id=${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(preferences)
        });

        const data = await response.json();

        if (data.status === "success") {
            alert("Preferences updated successfully!");
        } else {
            alert("Failed to update preferences.");
        }
    } catch (error) {
        console.error('Error updating user preferences:', error);
        alert("Error updating preferences.");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, setting up search...');
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const searchType = document.getElementById('search-type');

    console.log('Elements found:', { searchButton: !!searchButton, searchInput: !!searchInput, searchType: !!searchType });

    let searchMode = 'title';

    if (searchType) {
        searchType.addEventListener('change', (e) => {
            searchMode = e.target.value;
            if (searchMode === 'genre') {
                searchInput.placeholder = 'Click search to find by your favorite genres';
                searchInput.disabled = true;
                searchInput.value = '';
            } else {
                searchInput.placeholder = 'Search for a movie...';
                searchInput.disabled = false;
            }
        });
    }

    if (searchButton) {
        console.log('Adding click listener to search button');
        searchButton.addEventListener('click', () => {
            console.log('Search button clicked, mode:', searchMode);
            if (searchMode === 'genre') {
                discoverMoviesByGenre();
            } else {
                loadMovies();
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                if (searchMode === 'genre') {
                    discoverMoviesByGenre();
                } else {
                    loadMovies();
                }
            }
        });
    }

    loadMovies('Avengers');
    createGenres("0b8ac00c-a52b-4649-bd75-699b49c00ce3");
});