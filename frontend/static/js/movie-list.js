// Cache configuration
const CACHE_CONFIG = {
    MOVIES_CACHE_KEY: 'moviesCache',
    GENRES_CACHE_KEY: 'genresCache',
    CACHE_DURATION: 30 * 60 * 1000 // 30 minutes in milliseconds
};

// Cache utility functions
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


// Funzione per ricostruire la lista dei film nel div
function renderMovies(movieListElement, movies, userGenres = []) {
    // Salva lo spinner prima di resettare il contenuto
    const spinner = document.getElementById('loading-spinner');
    const spinnerParent = spinner.parentNode;
    spinner.remove(); // Rimuove temporaneamente lo spinner
    
    movieListElement.innerHTML = ''; // Resetta il contenuto del div
    movieListElement.appendChild(spinner); // Reinserisce lo spinner
    
    movies.forEach((movie, index) => {
        // console.log(`Rendering movie ${index + 1}:`, {
        //     title: movie.Title || movie.title,
        //     id: movie.imdbID || movie.id,
        //     genres: movie.genre_ids || movie.Genre,
        //     fullMovieData: movie
        // });
        if (!movie) return; // Salta se il film non è valido

        const movieItem = document.createElement('div');
        movieItem.classList.add('movie-item');

        const posterUrl = movie.Poster !== 'N/A' ? movie.Poster : 'https://via.placeholder.com/50x75';
        const genreNames = (movie.genre_ids || [])
            .map(id => {
                const genre = userGenres.find(g => g.genreId === id);
                return genre ? genre.name : null;
            })
            .filter(name => name) // Rimuove i valori null
            .join(', ') || movie.Genre || 'N/A';

        movieItem.innerHTML = `
            <img src="${posterUrl}" alt="${movie.Title || movie.title || 'Movie poster'}">
            <div class="movie-info">
                <div class="title">${movie.Title || movie.title || 'Unknown'} (${movie.Year || (movie.release_date ? movie.release_date.split('-')[0] : 'N/A')})</div>
                <div class="details">
                    <div><strong>Genre:</strong> ${genreNames}</div>
                    <div><strong>Rating:</strong> ${movie.imdbRating || movie.vote_average || 'N/A'}</div>
                    <div><strong>IMDb:</strong> ${movie.imdbID || 'N/A'}</div>
                </div>
            </div>
        `;

        movieItem.onclick = () => {
            window.location.href = `/movie?id=${movie.imdbID || movie.id}`;
        };

        movieListElement.appendChild(movieItem);
    });
}

async function loadMovies(query = '') {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    const searchQuery = query || searchInput.value;

    if (!searchQuery) {
        alert('Please enter a movie title!');
        return;
    }

    // Check cache first
    const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.MOVIES_CACHE_KEY, searchQuery);
    const cachedMovies = cacheUtils.get(cacheKey);
    
    if (cachedMovies) {
        renderMovies(movieList, cachedMovies);
        return;
    }

    spinner.style.display = 'block';
    searchButton.disabled = true;

    try {
        const response = await fetch(`http://localhost:5017/api/v1/movies/search-by-text?query=${encodeURIComponent(searchQuery)}`);
        const data_json = await response.json();

        if (!response.ok || data_json.status === 'fail') {
            throw new Error(data_json.message || 'Movies not found');
        }

        // Cache the results
        cacheUtils.set(cacheKey, data_json.data.movie_list);
        renderMovies(movieList, data_json.data.movie_list);
    } catch (error) {
        console.error('Error loading movies:', error);
        movieList.innerHTML = '';
        const errorMessage = document.createElement('div');
        errorMessage.textContent = 'Error loading movies. Please try again.';
        movieList.appendChild(errorMessage);
    } finally {
        spinner.style.display = 'none';
        searchButton.disabled = false;
    }
}

// Funzione per scoprire film tramite generi
async function discoverMoviesByGenre() {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchButton = document.getElementById('search-button');

    spinner.style.display = 'block';
    searchButton.disabled = true;

    try {
        const userGenres = await fetch(`http://localhost:5017/api/v1/user-genres?user_id=0b8ac00c-a52b-4649-bd75-699b49c00ce3`);
        const genresData = await userGenres.json();
        
        const preferredGenres = genresData.data.user_genres
            .filter(genre => genre.isPreferred)
            .map(genre => genre.genreId)
            .join(',');

        if (!preferredGenres) {
            alert('No preferred genres found!');
            spinner.style.display = 'none';
            searchButton.disabled = false;
            return;
        }

        // Check cache first
        const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.MOVIES_CACHE_KEY, `genres_${preferredGenres}`);
        const cachedMovies = cacheUtils.get(cacheKey);
        
        if (cachedMovies) {
            renderMovies(movieList, cachedMovies, genresData.data.user_genres);
            spinner.style.display = 'none';
            searchButton.disabled = false;
            return;
        }

        const response = await fetch(`http://localhost:5017/api/v1/movies/search-by-genre?with_genres=${preferredGenres}`);
        const data = await response.json();

        spinner.style.display = 'none';
        searchButton.disabled = false;

        if (data.status === "success" && data.data.movie_list) {
            // Cache the results
            cacheUtils.set(cacheKey, data.data.movie_list);
            renderMovies(movieList, data.data.movie_list, genresData.data.user_genres);
        } else {
            movieList.innerHTML = '';
            const noMoviesMessage = document.createElement('div');
            noMoviesMessage.textContent = 'No movies found.';
            movieList.appendChild(noMoviesMessage);
        }
    } catch (error) {
        console.error('Error discovering movies:', error);
        spinner.style.display = 'none';
        searchButton.disabled = false;
        movieList.innerHTML = '';
        const errorMessage = document.createElement('div');
        errorMessage.textContent = 'Error discovering movies. Please try again.';
        movieList.appendChild(errorMessage);
    }
}





async function createGenres(userId) {
    const genreTagsContainer = document.getElementById('genre-tags');

    // Check cache first
    const cacheKey = cacheUtils.getCacheKey(CACHE_CONFIG.GENRES_CACHE_KEY, userId);
    const cachedGenres = cacheUtils.get(cacheKey);

    if (cachedGenres) {
        renderGenreTags(genreTagsContainer, cachedGenres, userId);
        return;
    }

    try {
        const response = await fetch(`http://localhost:5017/api/v1/user-genres?user_id=${userId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch user genres');
        }

        if (data.status === 'fail') {
            throw new Error(data.message || 'Genres not found');
        }

        const userGenres = data.data.user_genres;
        
        // Cache the results
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

// Helper function to setup confirm button
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
            // Update cache after preferences change
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
            body: JSON.stringify(preferences )
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
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const dropdownButton = document.getElementById('dropdown-button');
    const dropdownMenu = document.getElementById('dropdown-menu');

    let searchMode = 'title';

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            if (searchMode === 'genre') {
                discoverMoviesByGenre();
            } else {
                loadMovies();
            }
        });
    }

    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', () => {
            dropdownMenu.classList.toggle('hidden');
        });

        dropdownMenu.addEventListener('click', (event) => {
            if (event.target.tagName === 'LI') {
                const selectedValue = event.target.getAttribute('data-value');
                searchMode = selectedValue;
                dropdownButton.textContent = event.target.textContent;
                dropdownMenu.classList.add('hidden');

                if (searchMode === 'genre') {
                    searchInput.value = 'The search will be based on your favorite genres';
                    searchInput.disabled = true;
                } else {
                    searchInput.value = '';
                    searchInput.disabled = false;
                }
            }
        });

        document.addEventListener('click', (event) => {
            if (!event.target.closest('.custom-dropdown')) {
                dropdownMenu.classList.add('hidden');
            }
        });
    }

    loadMovies('Avengers');
    createGenres("0b8ac00c-a52b-4649-bd75-699b49c00ce3");
});
