-- Users table (keep for adapter)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    preferences INTEGER[] DEFAULT '{}',
    password VARCHAR(255) NOT NULL
);
-- Create anon role for PostgREST
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'my_db_user') THEN
        CREATE ROLE my_db_user WITH LOGIN PASSWORD 'my_password';
    END IF;
END
$$;
GRANT USAGE ON SCHEMA public TO my_db_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO my_db_user;
ALTER ROLE my_db_user SET search_path = "my_db_user", public;
-- Genres table (PostgREST-managed)
CREATE TABLE genres (
    genre_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
-- Seed 28 TMDB genres
INSERT INTO genres (genre_id, name) VALUES 
    (28, 'Action'), 
    (12, 'Adventure'), 
    (16, 'Animation'),
    (35, 'Comedy'), 
    (80, 'Crime'), 
    (99, 'Documentary'),
    (18, 'Drama'), 
    (10751, 'Family'), 
    (14, 'Fantasy'),
    (36, 'History'), 
    (27, 'Horror'), 
    (10402, 'Music'),
    (9648, 'Mystery'),
    (10749, 'Romance'), 
    (878, 'Science Fiction'),
    (10770, 'TV Movie'), 
    (53, 'Thriller'), 
    (10752, 'War'),
    (37, 'Western') 
---
