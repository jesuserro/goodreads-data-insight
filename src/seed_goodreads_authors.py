import pandas as pd
from sqlalchemy import create_engine
import configparser

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
df = pd.read_csv('data/authors.csv')

# Renombrar columnas para que coincidan con la estructura de la tabla goodreads_authors
df.columns = [
    'author_id', 'name', 'workcount', 'fan_count', 'gender', 'image_url', 'about', 
    'born', 'died', 'influence', 'average_rate', 'rating_count', 'review_count', 
    'website', 'twitter', 'genre', 'original_hometown', 'country', 'latitude', 'longitude'
]

# Insertar datos en la tabla goodreads_authors
df.to_sql('goodreads_authors', engine, if_exists='append', index=False)