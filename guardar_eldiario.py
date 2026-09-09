import json
import os
import logging
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from eldiario_urls import obtener_urls_noticias
from eldiario_scraper import obtener_noticia


RUTA_JSON = "data/eldiario/noticias.json"
RUTA_LOG = "logs/eldiario_scraper.log"

LIMITE_NOTICIAS = 100


# ============================================================
# CONFIGURACIÓN DEL LOG
# ============================================================

os.makedirs(
    os.path.dirname(RUTA_LOG),
    exist_ok=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            RUTA_LOG,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================
# CARGAR NOTICIAS
# ============================================================

def cargar_noticias():

    if not os.path.exists(RUTA_JSON):

        logger.info(
            "El archivo JSON todavía no existe. "
            "Se iniciará una colección nueva."
        )

        return []

    try:

        with open(
            RUTA_JSON,
            "r",
            encoding="utf-8"
        ) as archivo:

            datos = json.load(archivo)

    except json.JSONDecodeError as e:

        raise Exception(
            f"El archivo JSON está corrupto: {e}"
        )

    except OSError as e:

        raise Exception(
            f"No se pudo leer el archivo JSON: {e}"
        )

    if not isinstance(datos, list):

        raise Exception(
            "El archivo JSON tiene una estructura inválida. "
            "Se esperaba una lista de noticias."
        )

    return datos

# ============================================================
# FECHA DE LA NOTICIA
# ============================================================

def fecha_noticia(noticia):

    fecha = noticia.get("fecha")

    if not fecha:

        return datetime.min

    try:

        return datetime.fromisoformat(
            fecha.replace("Z", "+00:00")
        ).replace(tzinfo=None)

    except (ValueError, TypeError):

        return datetime.min


# ============================================================
# GUARDAR NOTICIAS
# ============================================================

def guardar_noticias():

    inicio = time.time()

    logger.info("=" * 60)
    logger.info("INICIO DE EJECUCION")
    logger.info("=" * 60)

    try:

        # =====================================================
        # CARGAR NOTICIAS EXISTENTES
        # =====================================================

        noticias_existentes = cargar_noticias()

        noticias_por_url = {
            noticia["url"]: noticia
            for noticia in noticias_existentes
            if noticia.get("url")
        }

        # =====================================================
        # OBTENER URLS NUEVAS
        # =====================================================

        urls = obtener_urls_noticias(
            limite=20
        )

        nuevas_urls = [
            noticia["url"]
            for noticia in urls
            if noticia["url"] not in noticias_por_url
        ]

        existentes = (
            len(urls) - len(nuevas_urls)
        )

        logger.info(
            f"Noticias encontradas: {len(urls)}"
        )

        logger.info(
            f"Noticias ya existentes: {existentes}"
        )

        logger.info(
            f"Noticias nuevas: {len(nuevas_urls)}"
        )

        # =====================================================
        # VARIABLES
        # =====================================================

        nuevas = 0

        errores = 0

        # =====================================================
        # SOLO ABRIR CHROMIUM SI HAY NOTICIAS NUEVAS
        # =====================================================

        if nuevas_urls:

            logger.info(
                "Iniciando navegador Chromium..."
            )

            with sync_playwright() as p:

                browser = p.chromium.launch(
                    headless=True
                )

                page = browser.new_page()

                try:

                    # =========================================
                    # PROCESAR NOTICIAS
                    # =========================================

                    for i, url in enumerate(
                        nuevas_urls,
                        1
                    ):

                        logger.info(
                            f"Procesando "
                            f"{i}/{len(nuevas_urls)}: "
                            f"{url}"
                        )

                        try:

                            inicio_noticia = time.time()

                            noticia = obtener_noticia(
                                url,
                                page,
                                logger
                            )

                            duracion_noticia = time.time() - inicio_noticia

                            noticias_por_url[url] = noticia

                            nuevas += 1

                            logger.info(
                                f"NOTICIA GUARDADA: {url}"
                            )

                            logger.info(
                                f"Procesamiento completado | "
                                f"Noticia {i}/{len(nuevas_urls)} | "
                                f"Tiempo total: {duracion_noticia:.2f} segundos"
                            )

                        except Exception as e:

                            errores += 1

                            logger.error(
                                f"ERROR AL SCRAPEAR: "
                                f"{url} | {e}"
                            )

                        except Exception as e:

                            errores += 1

                            logger.error(
                                f"ERROR AL SCRAPEAR: "
                                f"{url} | {e}"
                            )

                finally:

                    browser.close()

                    logger.info(
                        "Chromium cerrado."
                    )

        else:

            logger.info(
                "No hay noticias nuevas. "
                "No se inicia Chromium."
            )

        # =====================================================
        # ORDENAR NOTICIAS
        # =====================================================

        noticias = list(
            noticias_por_url.values()
        )

        noticias.sort(
            key=fecha_noticia,
            reverse=True
        )

        noticias = noticias[
            :LIMITE_NOTICIAS
        ]

        # =====================================================
        # CREAR DIRECTORIO
        # =====================================================

        os.makedirs(
            os.path.dirname(RUTA_JSON),
            exist_ok=True
        )

        # =====================================================
        # GUARDAR JSON
        # =====================================================

        RUTA_TEMP = RUTA_JSON + ".tmp"

        with open(RUTA_TEMP, "w", encoding="utf-8") as archivo:
            json.dump(
                noticias,
                archivo,
                ensure_ascii=False,
                indent=4
            )
            archivo.flush()
            os.fsync(archivo.fileno())

        os.replace(RUTA_TEMP, RUTA_JSON)
        
        # =====================================================
        # LOG FINAL
        # =====================================================

        duracion = time.time() - inicio

        logger.info(
            f"Noticias nuevas: {nuevas}"
        )

        logger.info(
            f"Errores: {errores}"
        )

        logger.info(
            f"Total en JSON: {len(noticias)}"
        )

        logger.info(
            f"Límite máximo: {LIMITE_NOTICIAS}"
        )

        logger.info(
            f"Archivo: {RUTA_JSON}"
        )

        logger.info(
            f"EJECUCION COMPLETADA | "
            f"Duracion: {duracion:.2f} segundos"
        )

        logger.info("=" * 60)

    except Exception as e:

        duracion = time.time() - inicio

        logger.exception(
            f"EJECUCION FALLIDA | "
            f"Duracion: {duracion:.2f} segundos"
        )

        raise


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    guardar_noticias()