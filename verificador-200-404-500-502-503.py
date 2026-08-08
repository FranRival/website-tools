import pandas as pd
import requests
import os
import time

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

TIMEOUT = 15
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
# COMPROBAR QUE EXISTE COLUMNA C
# ============================================================

if len(df.columns) < 3:
    print("ERROR: El Excel no tiene una columna C.")
    input("\nPresiona ENTER para salir...")
    exit()


# ============================================================
# TOMAR SOLAMENTE COLUMNA C
# ============================================================

columna_c = df.columns[2]

print(f"\nProcesando columna C: {columna_c}")


# ============================================================
# VERIFICAR CADA URL
# ============================================================

resultados = []

total = len(df)

print(f"Total de URLs: {total}\n")


for numero, url in enumerate(df[columna_c], start=1):

    print(f"[{numero}/{total}] {url}")

    resultado = verificar_url(url)

    resultados.append(resultado)

    print(f"    -> {resultado}")

    time.sleep(PAUSA)


# ============================================================
# CREAR COLUMNA D
# ============================================================

df.insert(
    3,
    "HTTP_STATUS",
    resultados
)


# ============================================================
# GUARDAR
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
