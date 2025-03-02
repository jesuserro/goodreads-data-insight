-- Autores con mejor rating promedio
WITH avg_stats AS (
    SELECT AVG(average_rate) AS C, AVG(review_count) AS m
    FROM goodreads_authors
)
SELECT name, 
       average_rate, 
       review_count, 
       (review_count / (review_count + avg_stats.m)) * average_rate + (avg_stats.m / (review_count + avg_stats.m)) * avg_stats.C AS weighted_rating
FROM goodreads_authors, avg_stats
ORDER BY weighted_rating DESC
LIMIT 10;

-- Autores con más reseñas
SELECT name, review_count
FROM goodreads_authors
ORDER BY review_count DESC
LIMIT 10;

-- Autores con más fans
SELECT name, fan_count
FROM goodreads_authors
ORDER BY fan_count DESC
LIMIT 10;

-- Autores más prolíficos
SELECT name, workcount
FROM goodreads_authors
ORDER BY workcount DESC
LIMIT 10;

-- Autores más influyentes
SELECT name, influence
FROM goodreads_authors
WHERE influence IS NOT NULL
ORDER BY LENGTH(influence) DESC
LIMIT 10;

-- Análisis de procedencia
SELECT country, COUNT(*) as author_count
FROM goodreads_authors
GROUP BY country
ORDER BY author_count DESC;