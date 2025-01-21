import { getUserGenres } from './genres.js';

function loadMovies(query = '') {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchInput = document.getElementById('search-input');

    const searchQuery = query || searchInput.value;

    if (!searchQuery) {
        alert('Please enter a movie title!');
        return;
    }

    movieList.innerHTML = '';
    movieList.appendChild(spinner);
    spinner.style.display = 'block';

    fetch(`http://localhost:5001/api/v1/search_info?title=${encodeURIComponent(searchQuery)}`)
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
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
                        console.log(`Selected movie: ${movie.imdbID}`);
                    };

                    movieList.appendChild(movieItem);
                });
            } else {
                movieList.innerHTML = 'No movies found.';
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error loading movies:', error);
            movieList.innerHTML = 'Error loading movies. Please try again.';
        });
}

async function createGenres(userId) {
    const genreTagsContainer = document.getElementById('genre-tags');

    try {
        // Chiama la funzione per ottenere i generi con `name` e `isPreferred`
        const userGenres = await getUserGenres(userId);

        // Pulisce il contenitore dei tag esistente
        genreTagsContainer.innerHTML = '';

        // Crea i tag basandosi sui generi ottenuti
        userGenres.forEach(genre => {
            const tag = document.createElement('div');
            tag.classList.add('genre-tag');
            tag.textContent = genre.name;

            // Aggiungi una classe se è un genere preferito
            if (genre.isPreferred) {
                tag.classList.add('selected');
            }

            // Aggiungi toggle per selezione/deselezione
            tag.onclick = () => {
                tag.classList.toggle('selected');
            };

            genreTagsContainer.appendChild(tag);
        });

        const confirmButton = document.getElementById('confirm-button');
        confirmButton.onclick = () => {
            // Ottieni i genreId selezionati
            const selectedGenres = Array.from(document.querySelectorAll('.genre-tag.selected'))
                .map(tag => {
                    // Trova il genere selezionato nella lista dei generi dell'utente
                    const genre = userGenres.find(g => g.name === tag.textContent);
                    return genre ? genre.genreId : null;
                })
                .filter(genreId => genreId !== null); // Filtra i generi non trovati

            if (selectedGenres.length > 0) {
                updateUserPreferences(userId, selectedGenres); // Chiamata all'API per aggiornare le preferenze
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
            body: JSON.stringify({ preferences })  // Passa solo la lista di generi selezionati
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

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add click event listener to search button
    const searchButton = document.getElementById('search-button');
    if (searchButton) {
        searchButton.addEventListener('click', () => loadMovies());
    }

    // Load initial movies and genres
    loadMovies('Avengers');
    createGenres("0b8ac00c-a52b-4649-bd75-699b49c00ce3");
});