import pandas as pd
from sqlalchemy import create_engine
import configparser
import re

# Leer el archivo de configuración
config = configparser.ConfigParser()
config.read('goodreads_config.cfg')

# Obtener las credenciales de la base de datos
db_user = config['database']['user']
db_password = config['database']['password']
db_host = config['database']['host']
db_name = config['database']['database']

# Crear conexión a la base de datos
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

# Leer el fichero CSV
df = pd.read_csv('data/goodreads_library_export.csv')

# Eliminar duplicados basados en 'Book Id'
df = df.drop_duplicates(subset=['Book Id'])

# Limpiar los valores de ISBN y ISBN13
def clean_isbn(isbn):
    if pd.isna(isbn) or isbn == '=""':
        return None
    return re.sub(r'^="|"$', '', isbn)

df['ISBN'] = df['ISBN'].apply(clean_isbn)
df['ISBN13'] = df['ISBN13'].apply(clean_isbn)

# Insertar datos en la tabla books
books_df = df[['Book Id', 'Title', 'ISBN', 'ISBN13', 'Average Rating', 'Publisher', 'Binding', 'Number of Pages', 'Year Published', 'Original Publication Year']]
books_df.columns = ['book_id', 'title', 'isbn', 'isbn13', 'average_rating', 'publisher', 'binding', 'number_of_pages', 'year_published', 'original_publication_year']
books_df.to_sql('books', engine, if_exists='append', index=False)

# Insertar datos en la tabla authors y book_authors
authors = set()
book_authors = []
for index, row in df.iterrows():
    author_names = row['Author'].split(',')
    for author_name in author_names:
        authors.add(author_name.strip())
        book_authors.append((row['Book Id'], author_name.strip()))

authors_df = pd.DataFrame(list(authors), columns=['name'])
authors_df.to_sql('authors', engine, if_exists='append', index=False)

# Obtener los IDs de los autores
author_ids_df = pd.read_sql('SELECT author_id, name FROM authors', engine)
author_ids_dict = dict(zip(author_ids_df['name'], author_ids_df['author_id']))

# Crear la lista de book_authors con author_id en lugar de author_name
book_authors_with_ids = [(book_id, author_ids_dict[author_name]) for book_id, author_name in book_authors]

book_authors_df = pd.DataFrame(book_authors_with_ids, columns=['book_id', 'author_id'])
book_authors_df.to_sql('book_authors', engine, if_exists='append', index=False)

# Reemplazar NaN en la columna Bookshelves con una cadena vacía
df['Bookshelves'] = df['Bookshelves'].fillna('')

# Insertar datos en la tabla bookshelves y book_bookshelves
bookshelves = set()
book_bookshelves = []
for index, row in df.iterrows():
    shelf_names = row['Bookshelves'].split(',')
    for shelf_name in shelf_names:
        bookshelves.add(shelf_name.strip())
        book_bookshelves.append((row['Book Id'], shelf_name.strip(), None))

bookshelves_df = pd.DataFrame(list(bookshelves), columns=['name'])
bookshelves_df.to_sql('bookshelves', engine, if_exists='append', index=False)

# Obtener los IDs de las estanterías
bookshelf_ids_df = pd.read_sql('SELECT bookshelf_id, name FROM bookshelves', engine)
bookshelf_ids_dict = dict(zip(bookshelf_ids_df['name'], bookshelf_ids_df['bookshelf_id']))

# Crear la lista de book_bookshelves con bookshelf_id en lugar de bookshelf_name
book_bookshelves_with_ids = [(book_id, bookshelf_ids_dict[bookshelf_name], position) for book_id, bookshelf_name, position in book_bookshelves]

book_bookshelves_df = pd.DataFrame(book_bookshelves_with_ids, columns=['book_id', 'bookshelf_id', 'position'])
book_bookshelves_df.to_sql('book_bookshelves', engine, if_exists='append', index=False)

# Reemplazar NaN en la columna Bookshelves with positions con una cadena vacía
df['Bookshelves with positions'] = df['Bookshelves with positions'].fillna('')

# Insertar datos en la tabla tags y book_tags
tags = set()
book_tags = []
for index, row in df.iterrows():
    tag_positions = row['Bookshelves with positions'].split(',')
    for tag_position in tag_positions:
        match = re.match(r'(.+?)\s+\(#(\d+)\)', tag_position.strip())
        if match:
            tag_name = match.group(1).strip()
            position = int(match.group(2).strip())
            tags.add(tag_name)
            book_tags.append((row['Book Id'], tag_name, position))

tags_df = pd.DataFrame(list(tags), columns=['name'])
tags_df.to_sql('tags', engine, if_exists='append', index=False)

# Obtener los IDs de las etiquetas
tag_ids_df = pd.read_sql('SELECT tag_id, name FROM tags', engine)
tag_ids_dict = dict(zip(tag_ids_df['name'], tag_ids_df['tag_id']))

# Crear la lista de book_tags con tag_id en lugar de tag_name
book_tags_with_ids = [(book_id, tag_ids_dict[tag_name], position) for book_id, tag_name, position in book_tags]

book_tags_df = pd.DataFrame(book_tags_with_ids, columns=['book_id', 'tag_id', 'position'])
book_tags_df.to_sql('book_tags', engine, if_exists='append', index=False)

# Insertar un único usuario en la tabla users
user_data = {'goodreads_user_id': [40291334], 'nombre': ['Jesús']}
users_df = pd.DataFrame(user_data)
users_df.to_sql('users', engine, if_exists='append', index=False)

# Obtener el user_id del usuario insertado
user_id_df = pd.read_sql('SELECT user_id FROM users WHERE goodreads_user_id = 40291334', engine)
user_id = user_id_df['user_id'].iloc[0]

# Insertar datos en la tabla reviews
reviews_df = df[['Book Id', 'Date Added', 'Date Read', 'My Rating', 'My Review', 'Bookshelves', 'Exclusive Shelf', 'Spoiler', 'Private Notes', 'Read Count', 'Owned Copies']]
reviews_df.columns = ['book_id', 'date_added', 'date_read', 'my_rating', 'my_review', 'bookshelves', 'exclusive_shelf', 'spoiler', 'private_notes', 'read_count', 'owned_copies']

# Añadir columnas adicionales usando assign
reviews_df = reviews_df.assign(goodreads_review_id=None, user_id=user_id)

# Reordenar columnas para que coincidan con la estructura de la tabla reviews
reviews_df = reviews_df[['goodreads_review_id', 'book_id', 'user_id', 'date_added', 'date_read', 'my_rating', 'my_review', 'bookshelves', 'exclusive_shelf', 'spoiler', 'private_notes', 'read_count', 'owned_copies']]

# Insertar datos en la tabla reviews y obtener los IDs generados
reviews_df.to_sql('reviews', engine, if_exists='append', index=False)

# Obtener los IDs de las reseñas
review_ids_df = pd.read_sql('SELECT review_id, book_id FROM reviews', engine)

# Insertar datos en la tabla book_reviews
book_reviews = [(row['book_id'], row['review_id']) for index, row in review_ids_df.iterrows()]
book_reviews_df = pd.DataFrame(book_reviews, columns=['book_id', 'review_id'])
book_reviews_df.to_sql('book_reviews', engine, if_exists='append', index=False)