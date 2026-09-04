import requests
from bs4 import BeautifulSoup
import json


def scrapear_noticia(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ==========================================
    # METADATOS
    # ==========================================

    og_title = soup.find("meta", property="og:title")
    og_description = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    author = soup.find("meta", attrs={"name": "author"})
    published = soup.find("meta", property="article:published_time")

    titulo = (
        og_title.get("content").strip()
        if og_title
        else None
    )

    descripcion = (
        og_description.get("content").strip()
        if og_description
        else None
    )

    imagen = (
        og_image.get("content").strip()
        if og_image
        else None
    )

    autor = (
        author.get("content").strip()
        if author
        else None
    )

    fecha = (
        published.get("content").strip()
        if published
        else None
    )

    # ==========================================
    # CATEGORÍA
    # ==========================================

    categoria = None

    schema = soup.find(
        "script",
        class_="yoast-schema-graph"
    )

    if schema:

        try:

            datos_schema = json.loads(
                schema.string
            )

            for item in datos_schema.get("@graph", []):

                if item.get("@type") == "Article":

                    secciones = item.get(
                        "articleSection"
                    )

                    if isinstance(secciones, list):
                        categoria = secciones[0]
                    else:
                        categoria = secciones

                    break

        except Exception:
            pass

    # ==========================================
    # CONTENIDO
    # ==========================================

    contenido_html = soup.select_one(
        ".content-inner"
    )

    parrafos = []

    if contenido_html:

        for p in contenido_html.find_all("p"):

            texto = p.get_text(
                " ",
                strip=True
            )

            if texto:
                parrafos.append(texto)

    contenido = "\n\n".join(parrafos)

    # ==========================================
    # RESULTADO
    # ==========================================

    noticia = {

        "titulo": titulo,

        "descripcion": descripcion,

        "contenido": contenido,

        "autor": autor,

        "fecha": fecha,

        "categoria": categoria,

        "imagen": imagen,

        "url": url

    }

    return noticia


# ==========================================
# PRUEBA
# ==========================================

if __name__ == "__main__":

    url = (
        "https://larazon.bo/nacional/2026/09/04/"
        "tribunal-rechaza-accion-de-libertad-de-"
        "cerimedo-y-allana-su-traslado/"
    )

    noticia = scrapear_noticia(url)

    print("\n========== NOTICIA ==========\n")

    print("Título:")
    print(noticia["titulo"])

    print("\nDescripción:")
    print(noticia["descripcion"])

    print("\nAutor:")
    print(noticia["autor"])

    print("\nFecha:")
    print(noticia["fecha"])

    print("\nCategoría:")
    print(noticia["categoria"])

    print("\nImagen:")
    print(noticia["imagen"])

    print("\nURL:")
    print(noticia["url"])

    print("\nContenido:")
    print(noticia["contenido"])