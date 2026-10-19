"""Librería educativa de robótica.

Primera etapa: transformaciones numéricas mediante NumPy.
"""

from .transforms import (Rot_RPY,Rot_RPY_grados,rad2deg,deg2rad,rotx,rotx3,roty,roty3,
rotz,rotz3,trans,Rot_eje, Eje_theta, Eje_theta_grados,RPY,RPY_grados,DH, H_inv, Rot_Q, Quaternions,
derivada_numerica_central, derivada_numerica, derivada_numerica2, interpolacion_tramos_vector,
interpolacion_lineal, interpolacion_lineal_vector, interpolacion_tramos, Energia_robot, ejes, Axis2Quaternions,
interpolacion_cubica, interpolacion_cubica_vector)
from .formatting import matriz_a_texto, mostrar_matriz
from .plotting import (eslabon, cilindro, cono, flecha, Sistema3D, tubo, tubo2, Sistema3Dbool, prisma_rectangular,
prisma_rectangularC, prisma_rectangularC2, piramide, linea_punteada, normaL2, Sistema, Load_STL, gripper,
giroZ, giro_z, eslabon_STL, esfera, ejes3D, distancia_z, DibujaPlano, desplazamiento_z)

__version__ = "1.0.5.1"

__all__ = [
    "rotx3", "roty3", "rotz3",
    "rotx", "roty", "rotz", "trans",
    "Rot_RPY", "Rot_RPY_grados", "rad2deg", "deg2rad", "Rot_eje",
    "matriz_a_texto", "mostrar_matriz", "Eje_theta", "Eje_theta_grados",
    "RPY", "RPY_grados", "DH", "H_inv", "eslabon", "cilindro", "cono", "flecha",
    "Sistema3D", "tubo", "tubo2", "Sistema3Dbool", "Rot_Q", "Quaternions", "prisma_rectangular",
    "prisma_rectangularC", "piramide", "prisma_rectangularC2", "linea_punteada", "normaL2", "Sistema",
    "Load_STL", "interpolacion_tramos_vector", "derivada_numerica2", "derivada_numerica", "derivada_numerica_central",
    "interpolacion_lineal", "interpolacion_lineal_vector", "interpolacion_tramos", "gripper", "giroZ", "giro_z",
    "eslabon_STL", "Energia_robot", "esfera", "ejes", "ejes3D", "distancia_z", "DibujaPlano", "desplazamiento_z",
    "Axis2Quaternions", "interpolacion_cubica_vector", "interpolacion_cubica"
]
