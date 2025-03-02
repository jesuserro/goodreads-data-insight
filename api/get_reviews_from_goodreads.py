import requests
import xml.etree.ElementTree as ET
import configparser  # Importamos la librería estándar para .ini/.cfg

def get_goodreads_reviews(
    user: int,
    key: str,
    version: int = 2,
    base_url: str = "https://www.goodreads.com"
) -> dict:
    """
    Llama al endpoint 'GET /review/list/{user}.xml' descrito en el OpenAPI y 
    devuelve un diccionario que refleja la estructura de 'GoodreadsResponse'.
    """
    endpoint = f"{base_url}/review/list/{user}.xml"
    params = {"key": key, "v": version}

    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Levanta excepción si status != 200

    root = ET.fromstring(response.content)

    goodreads_dict = {
        "Request": {},
        "reviews": {}
    }

    # Parsear <Request>
    request_elem = root.find("Request")
    if request_elem is not None:
        goodreads_dict["Request"]["authentication"] = request_elem.findtext("authentication")
        goodreads_dict["Request"]["key"] = request_elem.findtext("key")
        goodreads_dict["Request"]["method"] = request_elem.findtext("method")

    # Parsear <reviews>
    reviews_elem = root.find("reviews")
    if reviews_elem is not None:
        goodreads_dict["reviews"]["start"] = reviews_elem.get("start")
        goodreads_dict["reviews"]["end"] = reviews_elem.get("end")
        goodreads_dict["reviews"]["total"] = reviews_elem.get("total")

        review_list = []
        for review_elem in reviews_elem.findall("review"):
            review_data = {
                "id": review_elem.findtext("id"),
                "rating": review_elem.findtext("rating"),
                "votes": review_elem.findtext("votes"),
                "spoiler_flag": review_elem.findtext("spoiler_flag"),
                "spoilers_state": review_elem.findtext("spoilers_state"),
                "started_at": review_elem.findtext("started_at"),
                "read_at": review_elem.findtext("read_at"),
                "date_added": review_elem.findtext("date_added"),
                "date_updated": review_elem.findtext("date_updated"),
                "read_count": review_elem.findtext("read_count"),
                "body": review_elem.findtext("body"),
                "comments_count": review_elem.findtext("comments_count"),
                "url": review_elem.findtext("url"),
                "link": review_elem.findtext("link"),
                "owned": review_elem.findtext("owned")
            }

            # Parsear <book>
            book_elem = review_elem.find("book")
            book_data = {}
            if book_elem is not None:
                book_data["id"] = book_elem.findtext("id")
                book_data["isbn"] = book_elem.findtext("isbn")
                book_data["isbn13"] = book_elem.findtext("isbn13")
                book_data["title"] = book_elem.findtext("title")
                book_data["image_url"] = book_elem.findtext("image_url")
                book_data["small_image_url"] = book_elem.findtext("small_image_url")
                book_data["average_rating"] = book_elem.findtext("average_rating")
                book_data["ratings_count"] = book_elem.findtext("ratings_count")

                # Autores
                authors_elem = book_elem.find("authors")
                if authors_elem is not None:
                    author_list = []
                    for author_elem in authors_elem.findall("author"):
                        author_data = {
                            "id": author_elem.findtext("id"),
                            "name": author_elem.findtext("name")
                        }
                        author_list.append(author_data)
                    book_data["authors"] = {"author": author_list}
                else:
                    book_data["authors"] = None

                # Work
                work_elem = book_elem.find("work")
                if work_elem is not None:
                    book_data["work"] = {"id": work_elem.findtext("id")}
                else:
                    book_data["work"] = None

            review_data["book"] = book_data

            # Parsear <shelves>
            shelves_elem = review_elem.find("shelves")
            if shelves_elem is not None:
                shelf_list = []
                for shelf_elem in shelves_elem.findall("shelf"):
                    shelf_data = {
                        "exclusive": shelf_elem.get("exclusive"),
                        "name": shelf_elem.get("name")
                    }
                    shelf_list.append(shelf_data)
                review_data["shelves"] = {"shelf": shelf_list}
            else:
                review_data["shelves"] = None

            review_list.append(review_data)

        goodreads_dict["reviews"]["review"] = review_list

    full_response = {"GoodreadsResponse": goodreads_dict}
    return full_response


if __name__ == "__main__":
    # 1) Crear el lector de configuración
    config = configparser.ConfigParser()
    
    # 2) Leer el archivo .cfg
    config.read("goodreads_config.cfg")  # O el nombre que hayas elegido

    # 3) Obtener valores de la sección [goodreads]
    user_id_str = config["goodreads"]["user_id"]  # Ojo: esto vendrá como string
    api_key = config["goodreads"]["api_key"]

    # 4) Convertir user_id a int si hace falta
    user_id = int(user_id_str)

    # 5) Llamar a la función
    data = get_goodreads_reviews(user_id, api_key)

    # 6) Imprimir o usar el resultado
    from pprint import pprint
    pprint(data)
