import json
import os

from sitemap import obtener_urls_noticias
from larazon_scraper import scrapear_noticia


RUTA_JSON = "data/larazon/noticias.json"


def cargar_noticias():

    if not os.path.exists(RUTA_JSON):
        return []

    try:

        with open(
            RUTA_JSON,
            "r",
            encoding="utf-8"
        ) as archivo:

            datos = json.load(archivo)

            if isinstance(datos, list):
                return datos

            return []

    except (json.JSONDecodeError, OSError):

        return []


def guardar_noticias():

    noticias_existentes = cargar_noticias()

    # Crear índice usando la URL
    noticias_por_url = {
        noticia["url"]: noticia
        for noticia in noticias_existentes
        if noticia.get("url")
    }

    # Obtener las 20 noticias más recientes
    urls = obtener_urls_noticias(limite=20)

    # Buscar solamente noticias que todavía no existen
    nuevas_urls = [
        url
        for url in urls
        if url not in noticias_por_url
    ]

    print()
    print("Noticias encontradas:", len(urls))
    print("Noticias ya existentes:", len(urls) - len(nuevas_urls))
    print("Noticias nuevas:", len(nuevas_urls))
    print()

    nuevas = 0
    errores = 0

    for i, url in enumerate(nuevas_urls, 1):

        print(f"Procesando {i}/{len(nuevas_urls)}...")
        print(url)

        try:

            noticia = scrapear_noticia(url)

            noticias_por_url[url] = noticia

            nuevas += 1

            print("NUEVA")

        except Exception as e:

            errores += 1

            print("ERROR:", e)

        print()

    # Convertir nuevamente a lista
    noticias = list(noticias_por_url.values())

    # Crear carpeta si no existe
    os.makedirs(
        os.path.dirname(RUTA_JSON),
        exist_ok=True
    )

    # Guardar JSON
    with open(
        RUTA_JSON,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            noticias,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    print("=" * 60)
    print("PROCESO TERMINADO")
    print("=" * 60)
    print()
    print("Noticias nuevas:", nuevas)
    print("Errores:", errores)
    print("Total en JSON:", len(noticias))
    print("Archivo:", RUTA_JSON)


if __name__ == "__main__":

    guardar_noticias()