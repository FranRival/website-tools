import pandas as pd
import requests
import os
import time

# ============================================================
# CONFIGURACIÓN
# ============================================================

ARCHIVO_ENTRADA = r"C:\ruta\de\tu\archivo.xlsx"
ARCHIVO_SALIDA = r"C:\ruta\de\tu\archivo_verificado.xlsx"

# Tiempo máximo de espera por URL
TIMEOUT = 15

# Pausa entre peticiones
PAUSA = 0.1


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
# TOMAR COLUMNA B
# ============================================================

if len(df.columns) < 2:
    print("ERROR: El Excel no tiene una columna B.")
    input("\nPresiona ENTER para salir...")
    exit()

columna_b = df.columns[1]


# ============================================================
# CREAR COLUMNA C
# ============================================================

resultados = []

total = len(df)

print(f"\nSe encontraron {total} URLs.")
print("Comenzando verificación...\n")


for numero, url in enumerate(df[columna_b], start=1):

    print(f"[{numero}/{total}] {url}")

    resultado = verificar_url(url)

    resultados.append(resultado)

    print(f"    -> {resultado}")

    time.sleep(PAUSA)


# ============================================================
# GUARDAR RESULTADOS EN COLUMNA C
# ============================================================

df.insert(
    2,
    "HTTP_STATUS",
    resultados
)


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

print(f"\nTotal de URLs: {total}")

print("\nResultados:")

print(df["HTTP_STATUS"].value_counts().to_string())

print("========================================")

input("\nPresiona ENTER para salir...")