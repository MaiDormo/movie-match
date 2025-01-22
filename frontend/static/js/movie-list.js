import { getUserGenres } from './genres.js';

function loadMovies(query = '') {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    const searchQuery = query || searchInput.value;

    if (!searchQuery) {
        alert('Please enter a movie title!');
        return;
    }

    movieList.innerHTML = '';
    movieList.appendChild(spinner);
    spinner.style.display = 'block';
    searchButton.disabled = true; // Disable the search button to prevent multiple clicks

    fetch(`http://localhost:5001/api/v1/search_info?title=${encodeURIComponent(searchQuery)}`)
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
            searchButton.disabled = false; // Re-enable the search button

            if (data.status === "success" && Array.isArray(data.data)) {
                data.data.forEach(movie => {
                    const movieItem = document.createElement('div');
                    movieItem.classList.add('movie-item');

                    movieItem.innerHTML = `
                        <img src="${movie.Poster !== "N/A" ? movie.Poster : 'https://via.placeholder.com/50x75'}" alt="${movie.Title}">
                        <div class="movie-info">
                            <div class="title">${movie.Title} (${movie.Year})</div>
                            <div class="details">
                                <div><strong>Genre:</strong> ${movie.Genre || 'N/A'}</div>
                                <div><strong>Rating:</strong> ${movie.imdbRating || 'N/A'}</div>
                                <div><strong>Type:</strong> ${movie.Type || 'N/A'}</div>
                                <div><strong>IMDb:</strong> ${movie.imdbID || 'N/A'}</div>
                            </div>
                        </div>
                    `;

                    movieItem.onclick = () => {
                        window.location.href = `/movie?id=${movie.imdbID}`;
                    };

                    movieList.appendChild(movieItem);
                });
            } else {
                movieList.innerHTML = 'No movies found.';
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            searchButton.disabled = false; // Re-enable the search button
            console.error('Error loading movies:', error);
            movieList.innerHTML = 'Error loading movies. Please try again.';
        });
}

async function getMovieImdbId(tmdbId, defaultImdbId = 'tt0111161') { // Default to "The Shawshank Redemption"
    try {
        console.log('http://localhost:5003/api/v1/find-id?id=${tmdbId}&language=en-US');
        const response = await fetch(`http://localhost:5003/api/v1/find-id?id=${tmdbId}&language=en-US`);
        const data = await response.json();

        if (response.ok && data.status === "success" && data.data && data.data.imdb_id) {
            window.location.href = `/movie?id=${data.data.imdb_id}`;
        } else {
            console.error('Error fetching IMDb ID:', data.message || 'Unknown error');
            console.warn('Falling back to default movie ID:', defaultImdbId);
            window.location.href = `/movie?id=${defaultImdbId}`;
        }
    } catch (error) {
        console.error('Error fetching IMDb ID:', error);
        console.warn('Falling back to default movie ID:', defaultImdbId);
        window.location.href = `/movie?id=${defaultImdbId}`;
    }
}

async function discoverMoviesByGenre() {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchButton = document.getElementById('search-button');

    movieList.innerHTML = '';
    movieList.appendChild(spinner);
    spinner.style.display = 'block';
    searchButton.disabled = true; // Disable the search button to prevent multiple clicks

    try {
        const userGenres = await getUserGenres("0b8ac00c-a52b-4649-bd75-699b49c00ce3");
        console.log('User genres:', userGenres);

        const preferredGenres = userGenres
            .filter(genre => genre.isPreferred)
            .map(genre => genre.genreId)
            .join(',');

        if (!preferredGenres) {
            alert('No preferred genres found!');
            spinner.style.display = 'none';
            searchButton.disabled = false; // Re-enable the search button
            return;
        }

        const response = await fetch(`http://localhost:5003/api/v1/discover-movies?language=en-EN&with_genres=${preferredGenres}&vote_avg_gt=7.0&sort_by=popularity.desc`);
        const data = await response.json();

        spinner.style.display = 'none';
        searchButton.disabled = false; // Re-enable the search button

        if (data.status === "success" && data.data?.results) {
            data.data.results.forEach(movie => {
                if (!movie) return; // Skip if movie is undefined

                const movieItem = document.createElement('div');
                movieItem.classList.add('movie-item');

                const posterUrl = movie.poster_path 
                    ? `https://image.tmdb.org/t/p/original${movie.poster_path}` 
                    : 'https://via.placeholder.com/50x75';

                const genreNames = (movie.genre_ids || [])
                    .map(id => {
                        const genre = userGenres.find(g => g.genreId === id);
                        return genre ? genre.name : null;
                    })
                    .filter(name => name) // Remove null values
                    .join(', ');

                movieItem.innerHTML = `
                    <img src="${posterUrl}" alt="${movie.title || 'Movie poster'}">
                    <div class="movie-info">
                        <div class="title">${movie.title || 'Unknown'} (${movie.release_date ? movie.release_date.split('-')[0] : 'N/A'})</div>
                        <div class="details">
                            <div><strong>Genre:</strong> ${genreNames || 'N/A'}</div>
                            <div><strong>Rating:</strong> ${movie.vote_average || 'N/A'}</div>
                        </div>
                    </div>
                `;

                // Add click event handler with error handling
                movieItem.addEventListener('click', async () => {
                        await getMovieImdbId(movie.id)
                    });

                movieList.appendChild(movieItem);
            });
        } else {
            movieList.innerHTML = 'No movies found.';
        }
    } catch (error) {
        console.error('Error discovering movies:', error);
        spinner.style.display = 'none';
        searchButton.disabled = false; // Re-enable the search button
        movieList.innerHTML = 'Error discovering movies. Please try again.';
    }
}

async function createGenres(userId) {
    const genreTagsContainer = document.getElementById('genre-tags');

    try {
        const userGenres = await getUserGenres(userId);
        genreTagsContainer.innerHTML = '';

        userGenres.forEach(genre => {
            const tag = document.createElement('div');
            tag.classList.add('genre-tag');
            tag.textContent = genre.name;

            if (genre.isPreferred) {
                tag.classList.add('selected');
            }

            tag.onclick = () => {
                tag.classList.toggle('selected');
            };

            genreTagsContainer.appendChild(tag);
        });

        const confirmButton = document.getElementById('confirm-button');
        confirmButton.onclick = () => {
            const selectedGenres = Array.from(document.querySelectorAll('.genre-tag.selected'))
                .map(tag => {
                    const genre = userGenres.find(g => g.name === tag.textContent);
                    return genre ? genre.genreId : null;
                })
                .filter(genreId => genreId !== null);

            if (selectedGenres.length > 0) {
                updateUserPreferences(userId, selectedGenres);
            } else {
                alert('No genres selected!');
            }
        };
    } catch (error) {
        console.error('Error creating genre tags:', error);
    }
}

async function updateUserPreferences(userId, preferences) {
    try {
        const response = await fetch(`http://localhost:5010/api/v1/user?id=${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ preferences })
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