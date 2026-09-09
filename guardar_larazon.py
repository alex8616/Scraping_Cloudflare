import json
import os
import logging
import time
from datetime import datetime

from sitemap import obtener_urls_noticias
from larazon_scraper import scrapear_noticia


RUTA_JSON = "data/larazon/noticias.json"
RUTA_LOG = "logs/larazon_scraper.log"

LIMITE_URLS = 20
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
# GUARDAR JSON DE FORMA SEGURA
# ============================================================

def guardar_json(noticias):

    os.makedirs(
        os.path.dirname(RUTA_JSON),
        exist_ok=True
    )

    ruta_temp = RUTA_JSON + ".tmp"

    try:

        with open(
            ruta_temp,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                noticias,
                archivo,
                ensure_ascii=False,
                indent=4
            )

            archivo.flush()
            os.fsync(
                archivo.fileno()
            )

        os.replace(
            ruta_temp,
            RUTA_JSON
        )

    except Exception:

        if os.path.exists(ruta_temp):

            try:
                os.remove(ruta_temp)

            except OSError:
                pass

        raise


# ============================================================
# GUARDAR NOTICIAS
# ============================================================

def guardar_noticias():

    inicio = time.time()

    logger.info("=" * 60)
    logger.info("INICIO DE EJECUCION")
    logger.info("=" * 60)

    try:

        # ----------------------------------------------------
        # CARGAR NOTICIAS EXISTENTES
        # ----------------------------------------------------

        noticias_existentes = cargar_noticias()

        noticias_por_url = {
            noticia["url"]: noticia
            for noticia in noticias_existentes
            if noticia.get("url")
        }

        # ----------------------------------------------------
        # OBTENER URLs NUEVAS
        # ----------------------------------------------------

        urls = obtener_urls_noticias(
            limite=LIMITE_URLS
        )

        nuevas_urls = [
            url
            for url in urls
            if url not in noticias_por_url
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

        nuevas = 0
        errores = 0

        # ----------------------------------------------------
        # SCRAPEAR NOTICIAS NUEVAS
        # ----------------------------------------------------

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

                noticia = scrapear_noticia(
                    url
                )

                noticias_por_url[url] = noticia

                nuevas += 1

                duracion_noticia = (
                    time.time() - inicio_noticia
                )

                logger.info(
                    f"NOTICIA GUARDADA: {url}"
                )

                logger.info(
                    f"Procesamiento completado | "
                    f"Noticia {i}/{len(nuevas_urls)} | "
                    f"Tiempo: "
                    f"{duracion_noticia:.2f} segundos"
                )

            except Exception as e:

                errores += 1

                logger.error(
                    f"ERROR AL SCRAPEAR: "
                    f"{url} | {e}"
                )

        # ----------------------------------------------------
        # ORDENAR NOTICIAS
        # ----------------------------------------------------

        noticias = list(
            noticias_por_url.values()
        )

        noticias.sort(
            key=fecha_noticia,
            reverse=True
        )

        # ----------------------------------------------------
        # LIMITAR A 100
        # ----------------------------------------------------

        noticias = noticias[
            :LIMITE_NOTICIAS
        ]

        # ----------------------------------------------------
        # GUARDAR JSON
        # ----------------------------------------------------

        guardar_json(
            noticias
        )

        # ----------------------------------------------------
        # RESUMEN
        # ----------------------------------------------------

        duracion = (
            time.time() - inicio
        )

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
            f"Límite máximo: "
            f"{LIMITE_NOTICIAS}"
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

        duracion = (
            time.time() - inicio
        )

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