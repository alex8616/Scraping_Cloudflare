import json
import os
import logging
import time
from datetime import datetime

from sitemap import obtener_urls_noticias
from larazon_scraper import scrapear_noticia


RUTA_JSON = "data/larazon/noticias.json"
RUTA_LOG = "logs/scraper.log"

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

    except (json.JSONDecodeError, OSError) as e:

        logger.error(
            f"No se pudo leer el JSON: {e}"
        )

        return []


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

        noticias_existentes = cargar_noticias()

        noticias_por_url = {
            noticia["url"]: noticia
            for noticia in noticias_existentes
            if noticia.get("url")
        }

        urls = obtener_urls_noticias(
            limite=20
        )

        nuevas_urls = [
            url
            for url in urls
            if url not in noticias_por_url
        ]

        existentes = len(urls) - len(nuevas_urls)

        logger.info(
            f"Noticias encontradas: {len(urls)}"
        )

        logger.info(
            f"Noticias ya existentes: {existentes}"
        )

        logger.info(
            f"Noticias nuevas: {len(nuevas_urls)}"
        )

        nuevas = 0
        errores = 0

        for i, url in enumerate(
            nuevas_urls,
            1
        ):

            logger.info(
                f"Procesando {i}/{len(nuevas_urls)}: {url}"
            )

            try:

                noticia = scrapear_noticia(
                    url
                )

                noticias_por_url[url] = noticia

                nuevas += 1

                logger.info(
                    f"NOTICIA GUARDADA: {url}"
                )

            except Exception as e:

                errores += 1

                logger.error(
                    f"ERROR AL SCRAPEAR: {url} | {e}"
                )

        noticias = list(
            noticias_por_url.values()
        )

        noticias.sort(
            key=fecha_noticia,
            reverse=True
        )

        noticias = noticias[:LIMITE_NOTICIAS]

        os.makedirs(
            os.path.dirname(RUTA_JSON),
            exist_ok=True
        )

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


if __name__ == "__main__":

    guardar_noticias()