import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


BASE_URL = "https://larazon.bo"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    )
}


def obtener_sitemaps_posts():

    url = f"{BASE_URL}/sitemap_index.xml"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "xml"
    )

    sitemaps = []

    for sitemap in soup.find_all("sitemap"):

        loc = sitemap.find("loc")
        lastmod = sitemap.find("lastmod")

        if not loc:
            continue

        url_sitemap = loc.get_text(strip=True)

        if "/post-sitemap" not in url_sitemap:
            continue

        fecha = None

        if lastmod:

            try:
                fecha = datetime.fromisoformat(
                    lastmod
                    .get_text(strip=True)
                    .replace("Z", "+00:00")
                )

            except ValueError:
                pass

        sitemaps.append({
            "url": url_sitemap,
            "fecha": fecha
        })

    fecha_minima = datetime.min.replace(
        tzinfo=timezone.utc
    )

    sitemaps.sort(
        key=lambda sitemap: sitemap["fecha"] or fecha_minima,
        reverse=True
    )

    return sitemaps


def obtener_noticias_sitemap(sitemap_url):

    response = requests.get(
        sitemap_url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "xml"
    )

    noticias = []

    for url_tag in soup.find_all("url"):

        loc = url_tag.find("loc")
        lastmod = url_tag.find("lastmod")

        if not loc:
            continue

        url_noticia = loc.get_text(strip=True)

        # Ignorar imágenes
        if "/wp-content/uploads/" in url_noticia:
            continue

        fecha = None

        if lastmod:

            try:
                fecha = datetime.fromisoformat(
                    lastmod
                    .get_text(strip=True)
                    .replace("Z", "+00:00")
                )

            except ValueError:
                pass

        noticias.append({
            "url": url_noticia,
            "fecha_sitemap": fecha
        })

    return noticias


def obtener_urls_noticias(limite=20):

    sitemaps = obtener_sitemaps_posts()

    noticias = []
    urls_vistas = set()

    fecha_minima = datetime.min.replace(
        tzinfo=timezone.utc
    )

    print("Sitemaps de posts encontrados:", len(sitemaps))
    print()

    for i, sitemap in enumerate(sitemaps):

        print(
            f"Consultando {i + 1}/{len(sitemaps)}: "
            f"{sitemap['url']}"
        )

        nuevas_noticias = obtener_noticias_sitemap(
            sitemap["url"]
        )

        for noticia in nuevas_noticias:

            url = noticia["url"]

            if url in urls_vistas:
                continue

            urls_vistas.add(url)

            noticias.append(noticia)

        # Ordenamos temporalmente
        noticias.sort(
            key=lambda noticia: (
                noticia["fecha_sitemap"]
                or fecha_minima
            ),
            reverse=True
        )

        # Si ya tenemos suficientes noticias,
        # comprobamos si podemos detenernos.
        if len(noticias) >= limite:

            noticias_seleccionadas = noticias[:limite]

            fecha_limite = (
                noticias_seleccionadas[-1]["fecha_sitemap"]
            )

            siguiente_fecha = None

            if i + 1 < len(sitemaps):

                siguiente_fecha = sitemaps[i + 1]["fecha"]

            # Si el siguiente sitemap es más antiguo
            # que nuestra noticia número 20,
            # ya no puede aportar una noticia más reciente.
            if (
                fecha_limite is not None
                and siguiente_fecha is not None
                and siguiente_fecha <= fecha_limite
            ):

                break

    noticias.sort(
        key=lambda noticia: (
            noticia["fecha_sitemap"]
            or fecha_minima
        ),
        reverse=True
    )

    noticias = noticias[:limite]

    return [
        noticia["url"]
        for noticia in noticias
    ]


if __name__ == "__main__":

    noticias = obtener_urls_noticias(limite=20)

    print()
    print("=" * 60)
    print("NOTICIAS SELECCIONADAS:", len(noticias))
    print("=" * 60)
    print()

    for i, url in enumerate(noticias, 1):

        print(f"{i}. {url}")