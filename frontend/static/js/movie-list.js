
import { getUserGenres }  from './genres.js';

function loadMovies(query = '') {
    const movieList = document.getElementById('movie-list');
    const spinner = document.getElementById('loading-spinner');
    const searchInput = document.getElementById('search-input');

    // Se la query è vuota, prendi il valore dell'input
    const searchQuery = query || searchInput.value;

    if (!searchQuery) {
        alert('Please enter a movie title!');
        return;
    }

    // Svuota la lista prima di aggiungere nuovi film
    movieList.innerHTML = '';

    // Aggiungi lo spinner all'interno di movie-list
    movieList.appendChild(spinner);
    spinner.style.display = 'block'; // Mostra lo spinner

    // Effettua la richiesta fetch con il parametro della ricerca
    fetch(`http://localhost:5001/api/v1/search_info?title=${encodeURIComponent(searchQuery)}`)
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none'; // Nascondi lo spinner
            if (data && data.length > 0) {
                data.forEach(movie => {
                    const movieItem = document.createElement('div');
                    movieItem.classList.add('movie-item');

                    movieItem.innerHTML = `
                        <img src="${movie.Poster !== "N/A" ? movie.Poster : 'https://via.placeholder.com/50x75'}" alt="${movie.Title}">
                        <div class="movie-info">
                            <div class="title">${movie.Title} (${movie.Year})</div>
                            <div class="details">
                                <div><strong>Genre:</strong> ${movie.Genre}</div>
                                <div><strong>Rating:</strong> ${movie.imdbRating}</div>
                            </div>
                        </div>
                    `;

                    movieItem.onclick = () => {
                        // Ricarica la pagina quando clicchi su un film
                        window.location.reload();
                    };

                    movieList.appendChild(movieItem);
                });
            } else {
                movieList.innerHTML = 'No movies found.';
            }
        })
        .catch(error => {
            spinner.style.display = 'none'; // Nascondi lo spinner in caso di errore
            console.error('Error loading movies:', error);
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


// Carica "Avengers" all'inizio

window.onload = () => {
    loadMovies('Avengers');
    createGenres("0b8ac00c-a52b-4649-bd75-699b49c00ce3");
};