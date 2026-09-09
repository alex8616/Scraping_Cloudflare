import re
from datetime import datetime
from playwright.sync_api import sync_playwright


URL = "https://www.eldiario.net/portal/"

PATRON_NOTICIA = re.compile(
    r"^https://www\.eldiario\.net/portal/"
    r"(\d{4})/(\d{2})/(\d{2})/"
    r"[^/]+/?$"
)


def obtener_urls_noticias(limite=20):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print(f"Abriendo: {URL}")

        response = page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print(
            "STATUS:",
            response.status if response else None
        )

        page.wait_for_timeout(5000)

        enlaces = page.locator("a").evaluate_all(
            """
            elements => elements.map(a => ({
                texto: a.innerText.trim(),
                url: a.href
            }))
            """
        )

        noticias = {}

        for enlace in enlaces:

            texto = enlace["texto"]
            url = enlace["url"]

            coincidencia = PATRON_NOTICIA.match(url)

            if not coincidencia:
                continue

            # Evitar duplicados
            if url in noticias:
                continue

            anio = int(coincidencia.group(1))
            mes = int(coincidencia.group(2))
            dia = int(coincidencia.group(3))

            fecha = datetime(
                anio,
                mes,
                dia
            )

            noticias[url] = {
                "titulo": texto,
                "url": url,
                "fecha_url": fecha
            }

        browser.close()

    # Ordenar por fecha.
    # Para noticias del mismo día mantenemos
    # el orden en que aparecen en la portada.
    noticias_ordenadas = sorted(
        noticias.values(),
        key=lambda x: x["fecha_url"],
        reverse=True
    )

    return noticias_ordenadas[:limite]


if __name__ == "__main__":

    noticias = obtener_urls_noticias(limite=20)

    print()
    print("=" * 80)
    print("URLS DE NOTICIAS")
    print("=" * 80)

    for i, noticia in enumerate(noticias, start=1):

        print()
        print(f"[{i}]")

        print("TITULO PORTADA:", noticia["titulo"] or "(sin texto)")

        print(
            "FECHA:",
            noticia["fecha_url"].strftime("%Y-%m-%d")
        )

        print("URL:", noticia["url"])

    print()
    print("=" * 80)
    print("TOTAL:", len(noticias))
    print("=" * 80)