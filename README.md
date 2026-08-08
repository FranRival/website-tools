# URL Tools

## `verificador-200-404-500-502-503.py`

Script de Python para verificar la accesibilidad de las URLs contenidas en un archivo Excel. El programa toma las URLs de la **columna C**, realiza una petición HTTP individual para cada URL y registra en la **columna D** el código de respuesta obtenido (`200`, `404`, `500`, `502`, `503`, etc.). Para evitar sobrecargar el servidor, incorpora una pausa aleatoria entre cada petición.

## `convertir.py`

Script de Python que convierte los títulos de posts o videos de un archivo Excel en URLs amigables. Toma los títulos de la **columna A**, elimina acentos y caracteres especiales, convierte los espacios en guiones y genera el resultado en la **columna B**, agregando la extensión `.html`. Por ejemplo, `Camino 56 hacia la vista de aguila` se convierte en `camino-56-hacia-la-vista-de-aguila.html`.
