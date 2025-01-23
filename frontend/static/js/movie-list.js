// Funzione per ricostruire la lista dei film nel div
function renderMovies(movieListElement, movies, userGenres = []) {
    // Salva lo spinner prima di resettare il contenuto
    const spinner = document.getElementById('loading-spinner');
    const spinnerParent = spinner.parentNode;
    spinner.remove(); // Rimuove temporaneamente lo spinner
    
    movieListElement.innerHTML = ''; // Resetta il contenuto del div
    movieListElement.appendChild(spinner); // Reinserisce lo spinner
    
    console.log('Total movies to render:', movies.length);
    
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
                    <div><strong>Type:</strong> ${movie.Type || 'N/A'}</div>
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

// Funzione per caricare film tramite titolo
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

    // Non svuotare completamente movieList, gestisci solo la visibilità dello spinner
    spinner.style.display = 'block';
    searchButton.disabled = true;

    try {
        const response = await fetch(`http://localhost:5016/api/v1/movie_search_text?query=${encodeURIComponent(searchQuery)}`);
        const data_json = await response.json();

        if (!response.ok || data_json.status === 'fail') {
            throw new Error(data_json.message || 'Movies not found');
        }

        spinner.style.display = 'none';
        searchButton.disabled = false;

        renderMovies(movieList, data_json.data.movie_list);
    } catch (error) {
        spinner.style.display = 'none';
        searchButton.disabled = false;
        console.error('Error loading movies:', error);
        movieList.innerHTML = '';
        const errorMessage = document.createElement('div');
        errorMessage.textContent = 'Error loading movies. Please try again.';
        movieList.appendChild(errorMessage);
    }
}

// Funzione per scoprire film tramite generi
async function discoverMoviesByGenre() {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchButton = document.getElementById('search-button');

    // Non svuotare completamente movieList, gestisci solo la visibilità dello spinner
    spinner.style.display = 'block';
    searchButton.disabled = true;

    try {
        const userGenres = await fetch(`http://localhost:5016/api/v1/user_genres?user_id=0b8ac00c-a52b-4649-bd75-699b49c00ce3`);
        const genresData = await userGenres.json();
        console.log('User genres:', userGenres);

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

        const response = await fetch(`http://localhost:5016/api/v1/movie_search_genre?language=en-EN&with_genres=${preferredGenres}&vote_avg_gt=7.0&sort_by=popularity.desc`);
        const data = await response.json();

        spinner.style.display = 'none';
        searchButton.disabled = false;

        if (data.status === "success" && data.data.movie_list) {
            renderMovies(movieList, data.data.movie_list, userGenres);
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

    try {

        const response = await fetch(`http://localhost:5016/api/v1/user_genres?user_id=${userId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch user genres');
        }

        if (data.status === 'fail') {
            throw new Error(data.message || 'Genres not found');
        }

        // Estrarre i generi dall'oggetto JSON
        const userGenres = data.data.user_genres;

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
