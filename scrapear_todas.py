from sitemap import obtener_urls_noticias
from larazon_scraper import scrapear_noticia


if __name__ == "__main__":

    urls = obtener_urls_noticias()

    print("Noticias encontradas:", len(urls))
    print()

    for i, url in enumerate(urls, 1):

        print("=" * 80)
        print(f"NOTICIA {i}/{len(urls)}")
        print("=" * 80)

        try:

            noticia = scrapear_noticia(url)

            print("Título:", noticia["titulo"])
            print("Categoría:", noticia["categoria"])
            print("Autor:", noticia["autor"])
            print("Fecha:", noticia["fecha"])
            print("Imagen:", noticia["imagen"])
            print("Párrafos:", len(noticia["contenido"].split("\n\n")))

        except Exception as e:

            print("ERROR:", e)

        print()