async function fetchGenres() {
    try {
        const response = await fetch("http://localhost:5015/api/v1/genres");
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === "success" && data.data && data.data.genres) {
            // Map the genres to extract the desired fields
            return data.data.genres.map(genre => ({
                genreId: genre.genreId,
                name: genre.name
            }));
        } else {
            throw new Error("Unexpected response structure");
        }
    } catch (error) {
        console.error("Error fetching genres:", error);
        return []; // Return an empty array in case of error
    }
}

async function fetchUserPreferences(userId) {
    try {
        const response = await fetch(`http://localhost:5010/api/v1/user?id=${userId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === "success" && data.data && Array.isArray(data.data.preferences)) {
            // Restituisci la lista dei preferences
            return data.data.preferences;
        } else {
            throw new Error("Unexpected response structure or missing preferences");
        }
    } catch (error) {
        console.error("Error fetching user preferences:", error);
        return []; // Restituisci un array vuoto in caso di errore
    }
}

export async function getUserGenres(userId) {
    try {
        // Chiamata alle due funzioni
        const [genres, preferences] = await Promise.all([fetchGenres(), fetchUserPreferences(userId)]);
        
        // Mappa i generi e aggiunge il flag di presenza nei preferences
        return genres.map(genre => ({
            genreId: genre.genreId,
            name: genre.name,
            isPreferred: preferences.includes(genre.genreId)
        }));
    } catch (error) {
        console.error("Error fetching user genres:", error);
        return []; // Restituisci un array vuoto in caso di errore
    }
}

// Esempio di utilizzo
getUserGenres("0b8ac00c-a52b-4649-bd75-699b49c00ce3").then(userGenres => console.log(userGenres));
