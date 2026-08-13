#!/usr/bin/env python3
"""
Descarga videos listados en un archivo Excel (.xlsx).
    Columna A: título del video
    Columna B: URL del archivo .mp4

Antes de cada descarga verifica el espacio libre en disco; si no alcanza,
detiene el proceso.

Para usarlo: edita las variables en la sección "CONFIGURACIÓN" más abajo
y luego ejecuta:
    python descargar_videos.py

Requisitos:
    pip install requests openpyxl pandas
"""

import os
import re
import shutil
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# ============================================================
# CONFIGURACIÓN — edita estas variables según tu caso
# ============================================================

RUTA_EXCEL = r"C:\ruta\a\tu\archivo.xlsx"       # Excel con col A = título, col B = URL
CARPETA_DESCARGA = r"C:\ruta\a\tu\carpeta"      # Carpeta donde se guardarán los videos
MIN_GB_LIBRES = 2.0                             # Espacio mínimo libre en disco (GB) para continuar
REINTENTOS_POR_VIDEO = 2                        # Reintentos si falla la descarga de un video

# ============================================================

CHUNK_SIZE = 1024 * 1024  # 1 MB
TIMEOUT = 30  # segundos para conectar/leer


def espacio_libre_gb(ruta: str) -> float:
    """Devuelve el espacio libre en disco (en GB) para la partición donde está `ruta`."""
    total, usado, libre = shutil.disk_usage(ruta)
    return libre / (1024 ** 3)


CARACTERES_INVALIDOS = r'[\\/:*?"<>|]'


def nombre_archivo_desde_titulo(titulo: str, indice: int) -> str:
    """Genera un nombre de archivo seguro a partir del título (columna A)."""
    titulo = str(titulo).strip() if titulo is not None else ""
    if not titulo or titulo.lower() == "nan":
        titulo = f"video_{indice:04d}"
    titulo = re.sub(CARACTERES_INVALIDOS, "_", titulo)  # quita caracteres no válidos en nombres de archivo
    titulo = titulo.strip(" .")  # Windows no permite espacios/puntos al final
    if not titulo.lower().endswith(".mp4"):
        titulo += ".mp4"
    return titulo


def leer_filas_excel(ruta_excel: Path):
    """
    Lee el Excel y devuelve una lista de tuplas (titulo, url).
    Columna A = título, columna B = URL. Se ignora la fila de encabezado
    si la celda B1 no parece una URL.
    """
    df = pd.read_excel(ruta_excel, header=None, dtype=str)

    filas = []
    for _, fila in df.iterrows():
        titulo = fila[0] if len(fila) > 0 else None
        url = fila[1] if len(fila) > 1 else None
        if url is None or str(url).strip().lower() == "nan":
            continue
        url = str(url).strip()
        if not url.lower().startswith(("http://", "https://")):
            # probablemente es la fila de encabezado (p.ej. "Título" / "URL")
            continue
        filas.append((titulo, url))
    return filas


def descargar_video(url: str, destino: Path, min_gb: float) -> bool:
    """
    Descarga un solo video con streaming, revisando el espacio en disco
    periódicamente durante la descarga (no solo al inicio).
    Devuelve True si se descargó correctamente, False si hubo error.
    """
    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
            resp.raise_for_status()

            total_bytes = int(resp.headers.get("content-length", 0))

            # Si conocemos el tamaño del archivo, verificamos que quepa
            if total_bytes > 0:
                libre_bytes = shutil.disk_usage(destino.parent).free
                margen = min_gb * (1024 ** 3)
                if libre_bytes - total_bytes < margen:
                    print(
                        f"  ✗ No hay espacio suficiente para este archivo "
                        f"({total_bytes / (1024**2):.1f} MB). Deteniendo proceso."
                    )
                    return None  # señal especial: sin espacio

            escrito = 0
            with open(destino, "wb") as f:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:
                        continue
                    f.write(chunk)
                    escrito += len(chunk)

                    # Revisión periódica del disco cada ~50 MB escritos
                    if escrito % (50 * 1024 * 1024) < CHUNK_SIZE:
                        if espacio_libre_gb(destino.parent) < min_gb:
                            print("  ✗ Espacio en disco agotado durante la descarga.")
                            f.close()
                            destino.unlink(missing_ok=True)
                            return None

            return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error al descargar: {e}")
        return False


def main():
    ruta_excel = Path(RUTA_EXCEL)
    if not ruta_excel.exists():
        print(f"No se encontró el archivo Excel: {ruta_excel}")
        sys.exit(1)

    carpeta_destino = Path(CARPETA_DESCARGA)
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    filas = leer_filas_excel(ruta_excel)

    print(f"Se encontraron {len(filas)} filas con URL en {ruta_excel}")
    print(f"Espacio libre actual: {espacio_libre_gb(carpeta_destino):.2f} GB")
    print(f"Mínimo requerido para continuar: {MIN_GB_LIBRES} GB\n")

    exitosos = 0
    fallidos = 0
    log_errores = carpeta_destino / "errores.log"

    for i, (titulo, url) in enumerate(filas, start=1):
        libre = espacio_libre_gb(carpeta_destino)
        if libre < MIN_GB_LIBRES:
            print(f"\n⚠ Espacio en disco insuficiente ({libre:.2f} GB libres). "
                  f"Deteniendo el proceso en la fila {i}/{len(filas)}.")
            break

        nombre = nombre_archivo_desde_titulo(titulo, i)
        destino_archivo = carpeta_destino / nombre

        if destino_archivo.exists():
            print(f"[{i}/{len(filas)}] Ya existe, se omite: {nombre}")
            exitosos += 1
            continue

        print(f"[{i}/{len(filas)}] Descargando: {url}  ->  {nombre}")

        resultado = None
        for intento in range(1, REINTENTOS_POR_VIDEO + 2):
            resultado = descargar_video(url, destino_archivo, MIN_GB_LIBRES)
            if resultado is True:
                break
            if resultado is None:
                # Sin espacio: no reintentar, cortar todo
                break
            print(f"  Reintentando ({intento}/{REINTENTOS_POR_VIDEO})...")
            time.sleep(2)

        if resultado is True:
            print(f"  ✓ Completado ({destino_archivo.stat().st_size / (1024**2):.1f} MB)")
            exitosos += 1
        elif resultado is None:
            with open(log_errores, "a", encoding="utf-8") as log:
                log.write(f"{url}\tSIN_ESPACIO\n")
            break
        else:
            fallidos += 1
            with open(log_errores, "a", encoding="utf-8") as log:
                log.write(f"{url}\tFALLO_DESCARGA\n")

    print(f"\nResumen: {exitosos} descargados, {fallidos} fallidos de {len(filas)} totales.")
    if log_errores.exists():
        print(f"Detalle de errores en: {log_errores}")


if __name__ == "__main__":
    main()
