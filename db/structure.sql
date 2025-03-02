-- ==================================================
-- 1. Crear la base de datos y seleccionarla
-- ==================================================
CREATE DATABASE IF NOT EXISTS goodreads_insights;
USE goodreads_insights;

-- ==================================================
-- 2. Eliminar tablas si ya existen (opcional)
--    Esto evita errores si el script se ejecuta varias veces
-- ==================================================
DROP TABLE IF EXISTS book_reviews;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS book_bookshelves;
DROP TABLE IF EXISTS bookshelves;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS book_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS goodreads_authors;

-- Tabla para almacenar información de los autores de Goodreads
CREATE TABLE goodreads_authors (
    author_id INT PRIMARY KEY,
    name VARCHAR(255),
    workcount INT,
    fan_count INT,
    gender VARCHAR(50),
    image_url VARCHAR(255),
    about TEXT,
    born DATE,
    died DATE,
    influence TEXT,  -- Cambiado de VARCHAR(255) a TEXT
    average_rate DECIMAL(3, 2),
    rating_count INT,
    review_count INT,
    website VARCHAR(255),
    twitter VARCHAR(50),
    genre VARCHAR(255),
    original_hometown VARCHAR(255),
    country VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

-- Tabla para almacenar información básica de los libros
CREATE TABLE books (
    book_id INT PRIMARY KEY,
    title VARCHAR(255),
    isbn VARCHAR(20),
    isbn13 VARCHAR(20),
    average_rating DECIMAL(3, 2),
    publisher VARCHAR(255),
    binding VARCHAR(50),
    number_of_pages INT,
    year_published INT,
    original_publication_year INT
);

-- Tabla para almacenar información de los autores
CREATE TABLE authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255)
);

-- Tabla para manejar la relación muchos a muchos entre libros y autores
CREATE TABLE book_authors (
    book_id INT,
    author_id INT,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

-- Tabla para almacenar información de las estanterías
CREATE TABLE bookshelves (
    bookshelf_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255)
);

-- Tabla para manejar la relación muchos a muchos entre libros y estanterías
CREATE TABLE book_bookshelves (
    book_id INT,
    bookshelf_id INT,
    position INT,
    PRIMARY KEY (book_id, bookshelf_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (bookshelf_id) REFERENCES bookshelves(bookshelf_id)
);

-- Tabla para almacenar información de los usuarios
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    goodreads_user_id INT,
    nombre VARCHAR(250)
);

-- Insertar el único usuario
INSERT INTO users (user_id, goodreads_user_id, nombre) VALUES (1, 40291334, 'Jesús');

-- Tabla para almacenar información de las reseñas
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    goodreads_review_id INT,
    book_id INT,
    user_id INT,
    date_added DATE,
    date_read DATE,
    my_rating DECIMAL(3, 2),
    my_review TEXT,
    bookshelves VARCHAR(1000),
    exclusive_shelf VARCHAR(50),
    spoiler BOOLEAN,
    private_notes TEXT,
    read_count INT,
    owned_copies INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- Tabla para manejar la relación muchos a muchos entre libros y reseñas
CREATE TABLE book_reviews (
    book_id INT,
    review_id INT,
    PRIMARY KEY (book_id, review_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (review_id) REFERENCES reviews(review_id)
);

-- Tabla para almacenar información de las etiquetas
CREATE TABLE tags (
    tag_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255)
);

-- Tabla para manejar la relación muchos a muchos entre libros y etiquetas
CREATE TABLE book_tags (
    book_id INT,
    tag_id INT,
    position INT,
    PRIMARY KEY (book_id, tag_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);