import json
import logging
import os

import requests


# ============================================================
# CONFIGURACIÓN
# ============================================================

# URL_BASE = "https://tukostv.sdmlabo.com"

URL_BASE = "http://127.0.0.1:8000"

TIMEOUT = 30


# ============================================================
# LOG
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# SUBIR JSON
# ============================================================

def subir_json(
    fuente,
    ruta_json
):
    """
    Sube un archivo JSON al servidor Laravel.

    fuente:
        larazon
        eldiario

    ruta_json:
        Ruta local del archivo noticias.json
    """

    token = os.getenv(
        "NEWS_UPLOAD_TOKEN"
    )

    if not token:

        raise Exception(
            "No existe la variable de entorno "
            "NEWS_UPLOAD_TOKEN."
        )

    if not os.path.exists(ruta_json):

        raise Exception(
            f"No existe el archivo JSON: {ruta_json}"
        )

    try:

        with open(
            ruta_json,
            "r",
            encoding="utf-8"
        ) as archivo:

            noticias = json.load(archivo)

    except json.JSONDecodeError as e:

        raise Exception(
            f"El JSON está corrupto: {e}"
        )

    except OSError as e:

        raise Exception(
            f"No se pudo leer el JSON: {e}"
        )

    if not isinstance(noticias, list):

        raise Exception(
            "El JSON debe contener una lista de noticias."
        )

    url = (
        f"{URL_BASE}/interno/noticias/{fuente}"
    )

    logger.info(
        f"Subiendo JSON | "
        f"Fuente: {fuente} | "
        f"Noticias: {len(noticias)}"
    )

    try:

        respuesta = requests.post(
            url,
            json=noticias,
            headers={
                "X-API-Token": token,
                "Accept": "application/json",
            },
            timeout=TIMEOUT
        )

    except requests.RequestException as e:

        raise Exception(
            f"No se pudo conectar con Laravel: {e}"
        )

    if not respuesta.ok:

        raise Exception(
            f"Laravel respondió HTTP "
            f"{respuesta.status_code}: "
            f"{respuesta.text}"
        )

    try:

        resultado = respuesta.json()

    except ValueError:

        raise Exception(
            "Laravel respondió algo que no es JSON."
        )

    if not resultado.get("ok"):

        raise Exception(
            f"Laravel rechazó la subida: "
            f"{resultado}"
        )

    logger.info(
        f"JSON SUBIDO CORRECTAMENTE | "
        f"Fuente: {fuente} | "
        f"Noticias: {resultado.get('noticias')}"
    )

    return resultado