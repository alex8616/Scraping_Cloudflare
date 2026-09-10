from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import json


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="TUKOS TV - API de Noticias",
    description="API para servir las noticias recopiladas por los scrapers.",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FUENTES DE NOTICIAS
# ============================================================

FUENTES = {
    "larazonnoticias": BASE_DIR / "data" / "larazon" / "noticias.json",
    "eldiarionoticias": BASE_DIR / "data" / "eldiario" / "noticias.json",

    # Futuras fuentes:
    # "eldebernoticias": BASE_DIR / "data" / "eldeber" / "noticias.json",
    # "unitelnoticias": BASE_DIR / "data" / "unitel" / "noticias.json",
}


# ============================================================
# FUNCIÓN PARA LEER NOTICIAS
# ============================================================

def cargar_noticias(ruta: Path):

    if not ruta.exists():
        raise HTTPException(
            status_code=404,
            detail="El archivo de noticias no existe."
        )

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            noticias = json.load(archivo)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="El archivo JSON está corrupto."
        )

    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo leer el archivo: {e}"
        )

    if not isinstance(noticias, list):
        raise HTTPException(
            status_code=500,
            detail="La estructura del archivo JSON no es válida."
        )

    return noticias


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.get("/")
def inicio():

    return {
        "proyecto": "TUKOS TV",
        "servicio": "API de Noticias",
        "estado": "activo",
        "fuentes": list(FUENTES.keys())
    }


# ============================================================
# RUTAS DE NOTICIAS
# ============================================================

@app.get("/{fuente}")
def obtener_noticias(fuente: str):

    if fuente not in FUENTES:
        raise HTTPException(
            status_code=404,
            detail="Fuente de noticias no encontrada."
        )

    ruta_json = FUENTES[fuente]

    noticias = cargar_noticias(ruta_json)

    return JSONResponse(
        content=noticias
    )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8765,
        reload=False
    )