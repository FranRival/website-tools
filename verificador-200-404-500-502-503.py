import pandas as pd
import requests
import os
import time
import random

# ============================================================
# CONFIGURACIÓN
# ============================================================

# ============================================================
# Peticiones por segundo: 2
# time.sleep(PAUSA)
# TIMEOUT = 15
# PAUSA = 0.5
#PAUSA ALEATORIA -
# ============================================================

ARCHIVO_ENTRADA = r"C:\ruta\de\tu\archivo.xlsx"
ARCHIVO_SALIDA = r"C:\ruta\de\tu\archivo_verificado.xlsx"

# Tiempo máximo de espera de cada petición
TIMEOUT = 15

# Tiempo ALEATORIO entre URLs
PAUSA_MIN = 0.5
PAUSA_MAX = 1.5


# ============================================================
# VERIFICAR URL
# ============================================================

def verificar_url(url):

    if pd.isna(url) or str(url).strip() == "":
        return ""

    url = str(url).strip()

    try:

        respuesta = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        return respuesta.status_code

    except requests.exceptions.Timeout:

        return "TIMEOUT"

    except requests.exceptions.ConnectionError:

        return "ERROR_CONEXION"

    except requests.exceptions.RequestException:

        return "ERROR"


# ============================================================
# COMPROBAR ARCHIVO
# ============================================================

if not os.path.exists(ARCHIVO_ENTRADA):

    print("ERROR: No se encontró el archivo:")
    print(ARCHIVO_ENTRADA)

    input("\nPresiona ENTER para salir...")
    exit()


# ============================================================
# LEER EXCEL
# ============================================================

print("Leyendo Excel...")

df = pd.read_excel(ARCHIVO_ENTRADA)


# ============================================================
# COMPROBAR COLUMNA C
# ============================================================

if len(df.columns) < 3:

    print("ERROR: El Excel no tiene una columna C.")

    input("\nPresiona ENTER para salir...")
    exit()


# ============================================================
# TOMAR COLUMNA C
# ============================================================

columna_c = df.columns[2]

print(f"\nColumna utilizada: C ({columna_c})")

total = len(df)

print(f"Total de URLs: {total}")

print(
    f"Pausa aleatoria entre URLs: "
    f"{PAUSA_MIN} - {PAUSA_MAX} segundos"
)

print("\nComenzando...\n")


# ============================================================
# VERIFICAR URLs
# ============================================================

resultados = []


for numero, url in enumerate(df[columna_c], start=1):

    print(f"[{numero}/{total}] {url}")

    resultado = verificar_url(url)

    resultados.append(resultado)

    print(f"    HTTP STATUS: {resultado}")

    # ========================================================
    # PAUSA ALEATORIA
    # ========================================================

    pausa = random.uniform(
        PAUSA_MIN,
        PAUSA_MAX
    )

    print(f"    Esperando {pausa:.2f} segundos...")

    time.sleep(pausa)


# ============================================================
# CREAR COLUMNA D
# ============================================================

df.insert(
    3,
    "HTTP_STATUS",
    resultados
)


# ============================================================
# GUARDAR EXCEL
# ============================================================

df.to_excel(
    ARCHIVO_SALIDA,
    index=False
)


# ============================================================
# RESUMEN
# ============================================================

print("\n========================================")
print(" VERIFICACIÓN TERMINADA")
print("========================================")

print(f"Archivo generado:")
print(ARCHIVO_SALIDA)

print(f"\nTotal procesado: {total}")

print("\nResultados:")

print(
    df["HTTP_STATUS"]
    .value_counts()
    .to_string()
)

print("========================================")

input("\nPresiona ENTER para salir...")
