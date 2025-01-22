/* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

const database = 'movie-match';
const collection = 'genres';

// The current database to use.
use(database);

// Create a new collection.
db.createCollection(collection);

// Insert genres into the collection
db[collection].insertMany([
    { "genreId": 28, "name": "Action" },
    { "genreId": 12, "name": "Adventure" },
    { "genreId": 16, "name": "Animation" },
    { "genreId": 35, "name": "Comedy" },
    { "genreId": 80, "name": "Crime" },
    { "genreId": 99, "name": "Documentary" },
    { "genreId": 18, "name": "Drama" },
    { "genreId": 10751, "name": "Family" },
    { "genreId": 14, "name": "Fantasy" },
    { "genreId": 36, "name": "History" },
    { "genreId": 27, "name": "Horror" },
    { "genreId": 10402, "name": "Music" },
    { "genreId": 9648, "name": "Mystery" },
    { "genreId": 10749, "name": "Romance" },
    { "genreId": 878, "name": "Science Fiction" },
    { "genreId": 10770, "name": "TV Movie" },
    { "genreId": 53, "name": "Thriller" },
    { "genreId": 10752, "name": "War" },
    { "genreId": 37, "name": "Western" },
]);

db[collection].createIndex({ "genreId": 1 }, { unique: true });

// Verify the insertion
db[collection].find().pretty();

db[collection].getIndexes();