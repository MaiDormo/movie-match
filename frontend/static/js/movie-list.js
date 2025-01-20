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

// Carica "Avengers" all'inizio
window.onload = () => loadMovies('Avengers');