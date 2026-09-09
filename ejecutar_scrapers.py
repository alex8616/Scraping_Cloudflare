import subprocess
import sys
import logging
import time
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

RUTA_LOG = BASE_DIR / "logs" / "ejecutar_scrapers.log"

SCRAPERS = [
    {
        "nombre": "El Diario",
        "archivo": "guardar_eldiario.py",
    },
    {
        "nombre": "La Razón",
        "archivo": "guardar_larazon.py",
    },

    # ========================================================
    # FUTURAS FUENTES
    # ========================================================

    # {
    #     "nombre": "El Deber",
    #     "archivo": "guardar_eldeber.py",
    # },

    # {
    #     "nombre": "Unitel",
    #     "archivo": "guardar_unitel.py",
    # },

]


# ============================================================
# LOGGING
# ============================================================

RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(RUTA_LOG, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================
# EJECUTAR SCRAPER
# ============================================================

def ejecutar_scraper(nombre, archivo):
    ruta_script = BASE_DIR / archivo

    if not ruta_script.exists():
        logger.error(
            "No existe el archivo del scraper: %s",
            ruta_script
        )
        return False

    logger.info("=" * 60)
    logger.info("INICIANDO: %s", nombre)
    logger.info("Archivo: %s", archivo)
    logger.info("=" * 60)

    inicio = time.time()

    try:
        resultado = subprocess.run(
            [sys.executable, str(ruta_script)],
            cwd=BASE_DIR
        )

        duracion = time.time() - inicio

        if resultado.returncode == 0:
            logger.info(
                "FINALIZADO: %s | Duracion: %.2f segundos",
                nombre,
                duracion
            )
            return True

        logger.error(
            "FALLO: %s | Codigo de salida: %s | Duracion: %.2f segundos",
            nombre,
            resultado.returncode,
            duracion
        )

        return False

    except Exception as e:
        duracion = time.time() - inicio

        logger.exception(
            "ERROR EJECUTANDO %s | Duracion: %.2f segundos | Error: %s",
            nombre,
            duracion,
            e
        )

        return False


# ============================================================
# EJECUTOR PRINCIPAL
# ============================================================

def main():
    inicio_total = time.time()

    logger.info("")
    logger.info("=" * 60)
    logger.info("INICIO DEL EJECUTOR DE SCRAPERS")
    logger.info("=" * 60)
    logger.info("Scrapers configurados: %d", len(SCRAPERS))
    logger.info("")

    resultados = []

    for scraper in SCRAPERS:
        nombre = scraper["nombre"]
        archivo = scraper["archivo"]

        exito = ejecutar_scraper(nombre, archivo)

        resultados.append({
            "nombre": nombre,
            "archivo": archivo,
            "exito": exito,
        })

        logger.info("")

    # ========================================================
    # RESUMEN
    # ========================================================

    exitosos = sum(1 for resultado in resultados if resultado["exito"])
    fallidos = len(resultados) - exitosos

    duracion_total = time.time() - inicio_total

    logger.info("=" * 60)
    logger.info("RESUMEN DE EJECUCION")
    logger.info("=" * 60)

    for resultado in resultados:
        estado = "OK" if resultado["exito"] else "ERROR"

        logger.info(
            "%s | %s | %s",
            estado,
            resultado["nombre"],
            resultado["archivo"]
        )

    logger.info("")
    logger.info("Total: %d", len(resultados))
    logger.info("Exitosos: %d", exitosos)
    logger.info("Fallidos: %d", fallidos)
    logger.info("Duracion total: %.2f segundos", duracion_total)

    logger.info("=" * 60)
    logger.info("FIN DEL EJECUTOR DE SCRAPERS")
    logger.info("=" * 60)

    # Si algún scraper falló, el proceso general devuelve código 1.
    # Esto será útil posteriormente para Windows Task Scheduler.
    if fallidos > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())