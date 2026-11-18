"""
Prueba básica de carga y visualización de archivos STL
utilizando SimpleRobotics.
"""

from pathlib import Path
import math

import numpy as np
import matplotlib.pyplot as plt

from SimpleRobotics import Load_STL, eslabon_STL


# Carpeta donde se encuentran los archivos STL.
CARPETA_STL = Path(__file__).resolve().parent / "STL_RR"

COLORES = {
    "Robot_2gdl_planar-Base.STL": [0.25, 0.55, 0.85],
    "Robot_2gdl_planar-Eslabon1.STL": [0.25, 0.70, 0.35],
    "Robot_2gdl_planar-Eslabon2.STL": [0.95, 0.60, 0.15],
    "Robot_2gdl_planar-Actuador.STL": [0.85, 0.30, 0.35],
}

# Buscar archivos STL, sin depender de sus nombres.
archivos = sorted(
    (
        archivo
        for archivo in CARPETA_STL.iterdir()
        if archivo.is_file() and archivo.suffix.lower() == ".stl"
    ),
    key=lambda archivo: archivo.name.lower()
)

if not archivos:
    raise FileNotFoundError(
        f"No se encontraron archivos STL en {CARPETA_STL}"
    )

# Una figura con dos columnas para comparar las mallas.
columnas = 2
filas = math.ceil(len(archivos) / columnas)

fig = plt.figure(figsize=(10, 5 * filas))

for i, archivo in enumerate(archivos, start=1):

    print(f"\nCargando: {archivo.name}")

    # 1. Cargar la malla mediante SimpleRobotics.
    solido = Load_STL(str(archivo))

    vertices = np.asarray(solido.vertices)
    caras = np.asarray(solido.faces)

    # 2. Comprobar que se hayan obtenido datos geométricos.
    if len(vertices) == 0 or len(caras) == 0:
        print("ERROR: la malla no contiene geometría.")
        continue

    # 3. Mostrar información básica del archivo.
    minimo = vertices.min(axis=0)
    maximo = vertices.max(axis=0)

    print(f"Vértices: {len(vertices)}")
    print(f"Triángulos: {len(caras)}")
    print(f"Coordenadas mínimas: {np.round(minimo, 4)}")
    print(f"Coordenadas máximas: {np.round(maximo, 4)}")
    print("Carga geométrica correcta.")

    # 4. Dibujar la malla sin desplazarla ni rotarla.
    ax = fig.add_subplot(
        filas, columnas, i, projection="3d"
    )

    color = COLORES.get(
    archivo.name,
    [0.7, 0.75, 0.85]
)

    eslabon_STL(
        np.eye(4),
        solido,
        color,
        ax=ax
    )

    ax.set_title(archivo.name)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # Mantener la proporción geométrica de la pieza.
    dimensiones = np.maximum(maximo - minimo, 1e-9)
    ax.set_box_aspect(dimensiones)

# Ocultar espacios vacíos si hay un número impar de piezas.
for j in range(len(archivos) + 1, filas * columnas + 1):
    ax = fig.add_subplot(filas, columnas, j, projection="3d")
    ax.set_visible(False)

fig.suptitle("Prueba de carga de archivos STL")
plt.tight_layout()
plt.show()