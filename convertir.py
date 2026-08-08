import pandas as pd
import re
import unicodedata
import os

# ============================================================
# CONFIGURACIÓN
# ============================================================

ARCHIVO_ENTRADA = r"C:\Users\dell\Downloads\suerte\Libro1.xlsx"
ARCHIVO_SALIDA = r"C:\Users\dell\Downloads\suerte\archivo_convertido.xlsx"


# ============================================================
# CONVERTIR TEXTO A URL
# ============================================================

def convertir_url(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).strip()

    # Minúsculas
    texto = texto.lower()

    # Eliminar acentos:
    # á -> a, é -> e, ñ -> n, etc.
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")

    # Apóstrofes: dog's -> dogs
    texto = texto.replace("'", "")
    texto = texto.replace("’", "")

    # Cualquier símbolo que no sea letra o número
    # se convierte en espacio
    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    # Espacios -> guiones
    texto = re.sub(r"\s+", "-", texto)

    # Eliminar guiones sobrantes
    texto = texto.strip("-")

    # Agregar extensión
    texto += ".html"

    return texto


# ============================================================
# LEER EXCEL
# ============================================================

if not os.path.exists(ARCHIVO_ENTRADA):
    print("ERROR: No se encontró el archivo:")
    print(ARCHIVO_ENTRADA)
    input("\nPresiona ENTER para salir...")
    exit()


print("Leyendo archivo...")
df = pd.read_excel(ARCHIVO_ENTRADA)


# ============================================================
# COLUMNA A -> COLUMNA B
# ============================================================

# Tomamos la primera columna (A)
columna_a = df.columns[0]

# Crear/reemplazar columna B
df.insert(
    1,
    "URL",
    df[columna_a].apply(convertir_url)
)


# ============================================================
# GUARDAR
# ============================================================

df.to_excel(ARCHIVO_SALIDA, index=False)

print("\n========================================")
print(" CONVERSIÓN TERMINADA")
print("========================================")
print(f"Archivo original : {ARCHIVO_ENTRADA}")
print(f"Archivo generado : {ARCHIVO_SALIDA}")
print(f"Registros        : {len(df)}")
print("========================================")

input("\nPresiona ENTER para salir...")