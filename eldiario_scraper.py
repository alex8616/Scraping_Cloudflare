import time

from playwright.sync_api import sync_playwright


MAX_REINTENTOS = 3
TIMEOUT = 60000
TIMEOUT_ARTICULO = 30000


def obtener_noticia(url, page, logger=None):

    inicio = time.time()

    ultimo_error = None

    for intento in range(1, MAX_REINTENTOS + 1):

        try:

            mensaje = (
                f"Abriendo noticia "
                f"(intento {intento}/{MAX_REINTENTOS}): {url}"
            )

            if logger:
                logger.info(mensaje)
            else:
                print(mensaje)

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=TIMEOUT
            )

            status = response.status if response else None

            if logger:
                logger.info(f"STATUS: {status}")
            else:
                print(f"STATUS: {status}")

            # =================================================
            # ESPERAR ARTÍCULO
            # =================================================

            article = page.locator("article").first

            article.wait_for(
                state="attached",
                timeout=TIMEOUT_ARTICULO
            )

            # =================================================
            # TITULO
            # =================================================

            titulo = ""

            elemento = article.locator("h1").first

            if elemento.count() > 0:
                titulo = elemento.inner_text().strip()

            # =================================================
            # DESCRIPCION
            # =================================================

            descripcion = ""

            elemento = article.locator(
                ".tdb_single_subtitle p"
            ).first

            if elemento.count() > 0:
                descripcion = elemento.inner_text().strip()

            # =================================================
            # FECHA
            # =================================================

            fecha = ""

            elemento = article.locator("time").first

            if elemento.count() > 0:

                fecha = (
                    elemento.get_attribute("datetime")
                    or elemento.inner_text().strip()
                )

            # =================================================
            # CATEGORIA
            # =================================================

            categoria = ""

            elemento = article.locator(
                "a.td-post-category"
            ).first

            if elemento.count() > 0:
                categoria = elemento.inner_text().strip()

            # =================================================
            # AUTOR
            # =================================================

            autor = ""

            elementos_autor = article.locator(
                ".td-post-content em"
            )

            if elementos_autor.count() > 0:
                autor = elementos_autor.last.inner_text().strip()

            # =================================================
            # IMAGEN
            # =================================================

            imagen = ""

            imagenes = article.locator("img")

            for i in range(imagenes.count()):

                img = imagenes.nth(i)

                src = (
                    img.get_attribute("src")
                    or img.get_attribute("data-src")
                    or ""
                )

                if src:
                    imagen = src
                    break

            # =================================================
            # CONTENIDO
            # =================================================

            contenido = []

            contenedor = article.locator(
                ".td-post-content"
            ).first

            if contenedor.count() > 0:

                parrafos = contenedor.locator("p")

                for i in range(parrafos.count()):

                    texto = parrafos.nth(
                        i
                    ).inner_text().strip()

                    if not texto:
                        continue

                    # No repetir el autor
                    if texto == autor:
                        continue

                    contenido.append(texto)

            contenido_final = "\n\n".join(
                contenido
            )

            # =================================================
            # VALIDACIÓN
            # =================================================

            if not titulo:
                raise Exception(
                    "La noticia no tiene título"
                )

            if not fecha:
                raise Exception(
                    "La noticia no tiene fecha"
                )

            if not contenido_final:
                raise Exception(
                    "La noticia no tiene contenido"
                )

            # =================================================
            # TIEMPO
            # =================================================

            duracion = time.time() - inicio

            if logger:

                logger.info(
                    f"Noticia extraída correctamente | "
                    f"Tiempo: {duracion:.2f} segundos"
                )

            else:

                print(
                    f"Noticia extraída correctamente | "
                    f"Tiempo: {duracion:.2f} segundos"
                )

            # =================================================
            # RESULTADO
            # =================================================

            return {
                "titulo": titulo,
                "descripcion": descripcion,
                "fecha": fecha,
                "categoria": categoria,
                "autor": autor,
                "imagen": imagen,
                "contenido": contenido_final,
                "url": url
            }

        except Exception as e:

            ultimo_error = e

            if logger:

                logger.warning(
                    f"ERROR intento "
                    f"{intento}/{MAX_REINTENTOS}: {e}"
                )

            else:

                print(
                    f"ERROR intento "
                    f"{intento}/{MAX_REINTENTOS}: {e}"
                )

            if intento < MAX_REINTENTOS:

                espera = intento * 2

                if logger:

                    logger.warning(
                        f"Reintentando en "
                        f"{espera} segundos..."
                    )

                else:

                    print(
                        f"Reintentando en "
                        f"{espera} segundos..."
                    )

                page.wait_for_timeout(
                    espera * 1000
                )

    duracion = time.time() - inicio

    raise Exception(
        f"No se pudo obtener la noticia después "
        f"de {MAX_REINTENTOS} intentos | "
        f"Tiempo: {duracion:.2f} segundos | "
        f"Último error: {ultimo_error}"
    )


# ============================================================
# PRUEBA INDIVIDUAL
# ============================================================

if __name__ == "__main__":

    URL = (
        "https://www.eldiario.net/portal/"
        "2026/09/09/"
        "la-pugna-de-poder-rodea-al-tigre/"
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:

            noticia = obtener_noticia(
                URL,
                page
            )

            print()
            print("=" * 80)
            print("NOTICIA EXTRAIDA")
            print("=" * 80)

            for campo, valor in noticia.items():

                print()
                print(f"{campo.upper()}:")
                print(valor)

            print()
            print("=" * 80)

        finally:

            browser.close()