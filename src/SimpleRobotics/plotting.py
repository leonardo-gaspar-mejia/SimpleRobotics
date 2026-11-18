from __future__ import annotations
from typing import Any
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from math import pi
from .transforms import rotx, roty, rotz, trans
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt

def _obtener_axes_3d(ax: Any = None) -> Any:
    """Obtiene un eje 3D existente sin crear figuras ni ejes nuevos."""

    if ax is not None:
        if not hasattr(ax, "get_zlim"):
            raise TypeError("ax debe ser un eje tridimensional.")
        return ax

    import matplotlib.pyplot as plt

    if not plt.get_fignums():
        raise RuntimeError("No hay una figura activa. Crea un eje 3D o proporciona el argumento ax")

    fig = plt.gcf()

    ax = next(
        (
            eje for eje in reversed(fig.axes)
            if hasattr(eje, "get_zlim")
        ),
        None,
    )

    if ax is None:
        raise RuntimeError(
            "Primero crea un eje 3D o proporciona el argumento ax."
        )

    return ax

def eslabon(po: Any, pf: Any, c: str= "k", lw: float = 2, *, ax: Any = None,) -> Any:

    # Obtener un eje 3D si no se cuenta con uno 

    ax = _obtener_axes_3d(ax)

    #Convertir los putnso a vectores numericos

    po = np.asanyarray(po, dtype=float).reshape(-1)
    pf = np.asanyarray(pf, dtype=float).reshape(-1)

    if po.size < 3 or pf.size < 3:
        raise ValueError("po y pf deben tener almenos 3 coordenadas.")

    #Equivalente a plot3 de MATLAB
    linea, = ax.plot([po[0], pf[0]],[po[1], pf[1]],[po[2], pf[2]],color=c,linewidth=lw,) 

    return linea
     
def cilindro(K: Any, alto: float, radio: float, dif: float, *, ax: Any = None, ) -> Any:

    #Dibuja un cilindro transformado por la matriz homogenea k

    import matplotlib.pyplot as plt

    #Obtener el eje 3D actual o crear uno si no existe

    ax = _obtener_axes_3d(ax)

    #Convertit la trasnformacion a una matriz numerica

    K = np.asanyarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("K Debe ser una matriz de transformacion 4x4")

    if alto < 0 or radio < 0:
        raise ValueError("alto y/o radio no pueden ser negativos")

    angulo = np.linspace(0, 2 * pi, 21)

    Xc = radio * np.cos(angulo)
    Yc = radio * np.sin(angulo)

    #Equivalente a zc = (Zc * alto) - dif.

    Zc1 = np.full_like(angulo, -dif)
    Zc2 = np.full_like(angulo, alto - dif)

    #Coordenadas homogeneas de la base y la cara superior 

    p1 = np.vstack((Xc, Yc, Zc1, np.ones_like(angulo))) 
    p2 = np.vstack((Xc, Yc, Zc2, np.ones_like(angulo))) 

    #Aplicar la transformacion K

    p1K = K @ p1
    p2K = K @ p2

    #Reconstruit las matrices que recibe la superficie 

    X = np.vstack((p1K[0, :], p2K[0, :]))
    Y = np.vstack((p1K[1, :], p2K[1, :]))
    Z = np.vstack((p1K[2, :], p2K[2, :]))

    #Color amarillo FANUC:  [255, 255, 50] / 255.
    color = (1.0, 1.0, 50 / 255)

    superficie = ax.plot_surface(X, Y, Z, color=color, linewidth = 0.3, antialiased = True,)

    return superficie

def tubo(K: Any, alto: float, radio: float, color: str, *, ax: Any = None,) -> Any:

    #Obtener el eje 3D actual o crear uno si no existe
    
    ax = _obtener_axes_3d(ax)

    #Convertit la trasnformacion a una matriz numerica

    K = np.asanyarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("K Debe ser una matriz de transformacion 4x4")

    if alto < 0 or radio < 0:
        raise ValueError("alto y/o radio no pueden ser negativos")

    angulo = np.linspace(0, 2 * pi, 21)

    Xc = radio * np.cos(angulo)
    Yc = radio * np.sin(angulo)

    #Equivalente a zc = (Zc * alto) - dif.

    Zc1 = np.full_like(angulo, 0)
    Zc2 = np.full_like(angulo, alto)

    #Coordenadas homogeneas de la base y la cara superior 

    p1 = np.vstack((Xc, Yc, Zc1, np.ones_like(angulo))) 
    p2 = np.vstack((Xc, Yc, Zc2, np.ones_like(angulo))) 

    #Aplicar la transformacion K

    p1K = K @ p1
    p2K = K @ p2

    #Reconstruit las matrices que recibe la superficie 

    X = np.vstack((p1K[0, :], p2K[0, :]))
    Y = np.vstack((p1K[1, :], p2K[1, :]))
    Z = np.vstack((p1K[2, :], p2K[2, :]))

    #Color amarillo FANUC:  [255, 255, 50] / 255.
    colores = {
        "red": (1, 0, 0),
        "green": (0, 1, 0),
        "blue": (0, 0, 1),
        "yellow": (1, 1, 0),
    }

    color_rgb = colores.get(color.lower())

    if color_rgb is not None:
        superficie = ax.plot_surface(
            X, Y, Z,
            color=color_rgb,
            linewidth=0.3,
            antialiased=True,
            shade=False,
        )
    else:
        superficie = ax.plot_surface(
            X, Y, Z,
            cmap="gray",
            linewidth=0.3,
            antialiased=True,
        )

    return superficie

def tubo2(K: Any, alto: float, radio: float, color: str, nalpha: float, *, ax: Any = None,) -> Any:

    # Validar la transparencia.
    if not 0.0 <= nalpha <= 1.0:
        raise ValueError(
            "nalpha debe estar entre 0 y 1."
        )


    superficie = tubo(K, alto, radio, color, ax=ax)

    superficie.set_alpha(nalpha)

    return superficie


def cono(K: Any, alto: float, radio: float, color: str, *, ax: Any = None,) -> Any:

    #Obtener el eje 3D actual o crear uno si no existe
    
    ax = _obtener_axes_3d(ax)

    #Convertit la trasnformacion a una matriz numerica

    K = np.asanyarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("K Debe ser una matriz de transformacion 4x4")

    if alto < 0 or radio < 0:
        raise ValueError("alto y/o radio no pueden ser negativos")

    angulo = np.linspace(0, 2 * pi, 21)

    #Circunferencia de la base

    xc = radio * np.cos(angulo)
    yc = radio * np.sin(angulo)


    Xc = np.vstack((xc, xc))
    Yc = np.vstack((yc, yc))
    Zc = np.vstack((np.zeros_like(angulo), np.ones_like(angulo)))

    zc = Zc * alto

    xc1 = Xc[0, :]
    yc1 = Yc[0, :]
    zc1 = zc[0, :]

    #Coordenadas homogeneas de la base y la cara superior 

    p1 = np.vstack((xc1, yc1, zc1, np.ones_like(angulo))) 
    p2 = np.vstack((np.zeros_like(angulo), np.zeros_like(angulo), np.full_like(angulo, alto), np.ones_like(angulo))) 

    #Aplicar la transformacion K

    p1K = K @ p1
    p2K = K @ p2

    #Reconstruit las matrices que recibe la superficie 

    X = np.vstack((p1K[0, :], p2K[0, :]))
    Y = np.vstack((p1K[1, :], p2K[1, :]))
    Z = np.vstack((p1K[2, :], p2K[2, :]))

    #Color amarillo FANUC:  [255, 255, 50] / 255.
    colores = {
        "red": (1, 0, 0),
        "green": (0, 1, 0),
        "blue": (0, 0, 1),
        "yellow": (1, 1, 0),
    }

    color_rgb = colores.get(color.lower())

    if color_rgb is not None:
        superficie = ax.plot_surface(
            X, Y, Z,
            color=color_rgb,
            linewidth=0.3,
            antialiased=True,
            shade=False,
        )
    else:
        superficie = ax.plot_surface(
            X, Y, Z,
            cmap="gray",
            linewidth=0.3,
            antialiased=True,
        )

    return superficie

def flecha(K: Any, alto: float, color: str, ax: Any = None) -> tuple[Any, Any]:

    #Obtener el eje 3D actual o crear uno si no existe
    
    ax = _obtener_axes_3d(ax)

    #Convertit la trasnformacion a una matriz numerica

    K = np.asanyarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("K Debe ser una matriz de transformacion 4x4")

    if alto <= 0:
        raise ValueError("alto no pueden ser negativos")

    #Proporciones de la flacha, equivalente a MATLAB

    radio1 = alto * 0.018
    radio2 = alto * 0.05
    alto1 = alto * 0.15
    alto2 = alto - alto1

    #Traslacion lical para colocar la punta sobre el tubo

    Tz = np.eye(4)
    Tz[2, 3] = alto2

    K_cono = K @ Tz

    #Dibujar el cuerpo de la flecha
    
    superficie_tubo = tubo(K, alto2, radio1, color, ax=ax)

    #Dibujar la punta de la flecha

    superficie_cono = cono(K_cono, alto1, radio2, color, ax=ax)

    return superficie_tubo, superficie_cono
  
def Sistema3D(M: Any, t: float, lx: str, ly: str, lz: str, tf: float, *, ax: Any = None) -> np.ndarray:
    #Dibuja un sistema de referencia tridimensional

    #Convertir M a una matriz numerica

    M = np.asanyarray(M, dtype=float)

    if M.shape != (4, 4):
        raise ValueError("K Debe ser una matriz de transformacion 4x4")

    if t <= 0:
        raise ValueError("t no pueden ser negativos o cero")

    #Obtener el eje 3D actual o crear uno si no existe
    
    ax = _obtener_axes_3d(ax)

    #Dibujar los tres ejes mediante flechas

    flecha(M @ roty(pi / 2), t, "red", ax = ax)
    flecha(M @ rotx(-pi / 2), t, "green", ax = ax)
    flecha(M, t, "blue", ax = ax)

    origen = M @ np.array([
        [0.0],
        [0.0],
        [0.0],
        [1.0],
    ])

    #posiciones de las etiquetas 
    tt = 1.1 * t

    posletrax = M @ np.array([tt, 0, 0, 1])
    posletray = M @ np.array([0, tt, 0, 1])
    posletraz = M @ np.array([0, 0, tt, 1])

    #Añadir las etiquetas utilizando notacion matematica

    if lx != " ":
        ax.text(
            posletrax[0],
            posletrax[1],
            posletrax[2],
            rf"${lx}$",
            fontsize=tf,
        )

    if ly != " ":
        ax.text(
            posletray[0],
            posletray[1],
            posletray[2],
            rf"${ly}$",
            fontsize=tf,
        )

    if lz != " ":
        ax.text(
            posletraz[0],
            posletraz[1],
            posletraz[2],
            rf"${lz}$",
            fontsize=tf,
        )

    return origen

def Sistema3Dbool(M: Any, t: float, lx: str, ly: str, lz: str, aparecer: Any, tf: float, *, ax: Any = None) -> np.ndarray:
    #Dibuja un sistema de referencia tridimensional

    #Convertir M a una matriz numerica

    M = np.asanyarray(M, dtype=float)

    if M.shape != (4, 4):
        raise ValueError("K Debe ser una matriz de transformacion 4x4")

    if t <= 0:
        raise ValueError("t no pueden ser negativos o cero")

    #Obtener el eje 3D actual o crear uno si no existe
    
    ax = _obtener_axes_3d(ax)

    #Dibujar los tres ejes mediante flechas

    if aparecer[0]:
        flecha(M @ roty(pi / 2), t, "red", ax = ax)

    if aparecer[1]:
        flecha(M @ rotx(-pi / 2), t, "green", ax = ax)

    if aparecer[2]:
        flecha(M, t, "blue", ax = ax)
    


    origen = M @ np.array([
        [0.0],
        [0.0],
        [0.0],
        [1.0],
    ])

    #posiciones de las etiquetas 
    tt = 1.2 * t

    posletrax = M @ np.array([tt, 0, 0, 1])
    posletray = M @ np.array([0, tt, 0, 1])
    posletraz = M @ np.array([0, 0, tt, 1])

    #Añadir las etiquetas utilizando notacion matematica

    if lx != " ":
        ax.text(
            posletrax[0],
            posletrax[1],
            posletrax[2],
            rf"${lx}$",
            fontsize=tf,
        )

    if ly != " ":
        ax.text(
            posletray[0],
            posletray[1],
            posletray[2],
            rf"${ly}$",
            fontsize=tf,
        )

    if lz != " ":
        ax.text(
            posletraz[0],
            posletraz[1],
            posletraz[2],
            rf"${lz}$",
            fontsize=tf,
        )

    return origen

def Sistema(M: Any, t: float, lx: str, ly: str, lz: str,tf: float, *, ax: Any = None) -> np.ndarray:

    #Dibuja un sistema de coordenadas 3D mediante líneas

    M = np.asarray(M, dtype=float)

    if M.shape != (4, 4):

        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    po = M @ np.array([[0], [0], [0], [1]], dtype=float )
    px = M @ np.array([[t], [0], [0], [1]], dtype=float )
    py = M @ np.array([[0], [t], [0], [1]], dtype=float )
    pz = M @ np.array([[0], [0], [t], [1]], dtype=float )

    ax.plot([po[0, 0], px[0, 0]], [po[1, 0], px[1, 0]], [po[2, 0], px[2, 0]], color = "r", linewidth = 2)

    ax.plot([po[0, 0], py[0, 0]], [po[1, 0], py[1, 0]], [po[2, 0], py[2, 0]], color = "g", linewidth = 2)

    ax.plot([po[0, 0], pz[0, 0]], [po[1, 0], pz[1, 0]], [po[2, 0], pz[2, 0]], color = "b", linewidth = 2)

    tt = 1.1 * t

    posletrax = M @ np.array([[tt], [0], [0], [1]], dtype=float)
    posletray = M @ np.array([[0], [tt], [0], [1]], dtype=float)
    posletraz = M @ np.array([[0], [0], [tt], [1]], dtype=float)

    ax.text(
        posletrax[0, 0], posletrax[1, 0], posletrax[2, 0],
        f"${lx}$", fontsize=tf
    )

    ax.text(
        posletray[0, 0], posletray[1, 0], posletray[2, 0],
        f"${ly}$", fontsize=tf
    )

    ax.text(
        posletraz[0, 0], posletraz[1, 0], posletraz[2, 0],
        f"${lz}$", fontsize=tf
    )

    return po

def prisma_rectangularC(K: Any, ancho_x: float, largo_y: float, alto_z: float, color: str, *, ax: Any = None) -> None:

    # Dibuja un prisma rectangular centrado en el origen

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    colores = {
        "red": (1, 0, 0),
        "blue": (0, 0, 1),
        "green": (0, 1, 0),
    }

    rgb = colores.get(color, (0.5, 0.5, 0.5))

    x1 = ancho_x /2
    x2 = -x1

    y1 = largo_y / 2
    y2 = -y1 

    z1 = alto_z /2 
    z2 = -z1

    XX = np.array([
        [x1, x1, x2, x2, x1],
        [x1, x1, x2, x2, x1]
    ], dtype=float)

    YY = np.array([
        [y1, y2, y2, y1, y1],
        [y1, y2, y2, y1, y1]
    ], dtype=float)

    ZZ = np.array([
        [z1, z1, z1, z1, z1],
        [z2, z2, z2, z2, z2]
    ], dtype=float)


    p1 = np.vstack((
        XX[0, :],
        YY[0, :],
        ZZ[0, :],
        np.ones(XX.shape[1])
    ))

    p2 = np.vstack((
        XX[1, :],
        YY[1, :],
        ZZ[1, :],
        np.ones(XX.shape[1])
    ))

    p1K = K @ p1
    p2K = K @ p2

    Xc = np.vstack((p1K[0, :], p2K[0, :]))
    Yc = np.vstack((p1K[1, :], p2K[1, :]))
    Zc = np.vstack((p1K[2, :], p2K[2, :]))

    
    ax.plot_surface(Xc, Yc, Zc, color=rgb, edgecolor = "none", shade = False)

    x1 = ancho_x /2
    x2 = -x1

    y1 = alto_z / 2
    y2 = -y1 

    z1 = largo_y /2 
    z2 = -z1

    XX = np.array([
        [x1, x1, x2, x2, x1],
        [x1, x1, x2, x2, x1]
    ], dtype=float)

    YY = np.array([
        [y1, y2, y2, y1, y1],
        [y1, y2, y2, y1, y1]
    ], dtype=float)

    ZZ = np.array([
        [z1, z1, z1, z1, z1],
        [z2, z2, z2, z2, z2]
    ], dtype=float)


    p1 = np.vstack((
        XX[0, :],
        YY[0, :],
        ZZ[0, :],
        np.ones(XX.shape[1])
    ))

    p2 = np.vstack((
        XX[1, :],
        YY[1, :],
        ZZ[1, :],
        np.ones(XX.shape[1])
    ))

    K2 = K @ rotx(-pi/2)

    p1K = K2 @ p1
    p2K = K2 @ p2

    Xc = np.vstack((p1K[0, :], p2K[0, :]))
    Yc = np.vstack((p1K[1, :], p2K[1, :]))
    Zc = np.vstack((p1K[2, :], p2K[2, :]))

    ax.plot_surface(Xc, Yc, Zc, color=rgb, edgecolor = "none", shade = False)

def prisma_rectangular(K: Any, ancho_x: float, largo_y: float, alto_z: float, color: str, *, ax: Any = None) -> None:

    prisma_rectangularC(K @ trans(0,0,alto_z/2),ancho_x,largo_y,alto_z,color, ax = ax)

def prisma_rectangularC2(K: Any, ancho_x: float, largo_y: float, alto_z: float, color: str,nalpha: float ,*, ax: Any = None) -> None:

    # Dibuja un prisma rectangular centrado en el origen

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    if not 0.0 <= nalpha <= 1.0:
        raise ValueError("nalpha debe estar entre 0 y 1.")

    colores = {
        "red": (1, 0, 0),
        "blue": (0, 0, 1),
        "green": (0, 1, 0),
    }

    rgb = colores.get(color, (0.5, 0.5, 0.5))

    x1 = ancho_x /2
    x2 = -x1

    y1 = largo_y / 2
    y2 = -y1 

    z1 = alto_z /2 
    z2 = -z1

    XX = np.array([
        [x1, x1, x2, x2, x1],
        [x1, x1, x2, x2, x1]
    ], dtype=float)

    YY = np.array([
        [y1, y2, y2, y1, y1],
        [y1, y2, y2, y1, y1]
    ], dtype=float)

    ZZ = np.array([
        [z1, z1, z1, z1, z1],
        [z2, z2, z2, z2, z2]
    ], dtype=float)


    p1 = np.vstack((
        XX[0, :],
        YY[0, :],
        ZZ[0, :],
        np.ones(XX.shape[1])
    ))

    p2 = np.vstack((
        XX[1, :],
        YY[1, :],
        ZZ[1, :],
        np.ones(XX.shape[1])
    ))

    p1K = K @ p1
    p2K = K @ p2

    Xc = np.vstack((p1K[0, :], p2K[0, :]))
    Yc = np.vstack((p1K[1, :], p2K[1, :]))
    Zc = np.vstack((p1K[2, :], p2K[2, :]))

    
    s1 = ax.plot_surface(Xc, Yc, Zc, color=rgb, edgecolor = "none", shade = False)

    s1.set_alpha(nalpha)

    x1 = ancho_x /2
    x2 = -x1

    y1 = alto_z / 2
    y2 = -y1 

    z1 = largo_y /2 
    z2 = -z1

    XX = np.array([
        [x1, x1, x2, x2, x1],
        [x1, x1, x2, x2, x1]
    ], dtype=float)

    YY = np.array([
        [y1, y2, y2, y1, y1],
        [y1, y2, y2, y1, y1]
    ], dtype=float)

    ZZ = np.array([
        [z1, z1, z1, z1, z1],
        [z2, z2, z2, z2, z2]
    ], dtype=float)


    p1 = np.vstack((
        XX[0, :],
        YY[0, :],
        ZZ[0, :],
        np.ones(XX.shape[1])
    ))

    p2 = np.vstack((
        XX[1, :],
        YY[1, :],
        ZZ[1, :],
        np.ones(XX.shape[1])
    ))

    K2 = K @ rotx(-pi/2)

    p1K = K2 @ p1
    p2K = K2 @ p2

    Xc = np.vstack((p1K[0, :], p2K[0, :]))
    Yc = np.vstack((p1K[1, :], p2K[1, :]))
    Zc = np.vstack((p1K[2, :], p2K[2, :]))

    s2 = ax.plot_surface(Xc, Yc, Zc, color=rgb, edgecolor = "none", shade = False)

    s2.set_alpha(nalpha)

def piramide(K: Any, alto: float, lado: float, color: str, *, ax: Any = None) -> None:

    # Dibuja una pirámide con el eje de simetría sobre Z,

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    colores = {
        "red": (1, 0, 0,),
        "blue": (0, 0, 1),
        "green": (0, 1, 0),
        "yellow": (1, 1, 0)
    }

    rgb = colores.get(color, (.5, .5, .5))

    radio = lado/np.sqrt(2)

    theta = np.linspace(0, 2 * pi, 5)

    Xc = np.vstack((
        radio * np.cos(theta),
        np.zeros_like(theta)
    ))

    Yc = np.vstack((
        radio * np.sin(theta),
        np.zeros_like(theta)
    ))

    Zc = np.vstack((
        np.zeros_like(theta),
        np.full_like(theta, alto)
    ))

    p1 = np.vstack((
        Xc[0, :],
        Yc[0, :],
        Zc[0, :],
        np.ones(Xc.shape[1])
    ))

    p2 = np.vstack((
        Xc[1, :],
        Yc[1, :],
        Zc[1, :],
        np.ones(Xc.shape[1])
    ))

    T = K @ rotz(pi / 4)

    p1K = T @ p1
    p2K = T @ p2

    Xc = np.vstack((p1K[0, :], p2K[0, :]))
    Yc = np.vstack((p1K[1, :], p2K[1, :]))
    Zc = np.vstack((p1K[2, :], p2K[2, :]))

    
    ax.plot_surface(Xc, Yc, Zc, color=rgb, edgecolor = "none", shade = False)

def normaL2(e: Any, t: Any) -> float:

    e = np.asarray(e, dtype=float)
    t = np.asarray(t, dtype=float).reshape(-1)

    if e.ndim != 2:
        raise ValueError("e debe ser un vector o una matriz de señales.")

    nmuestras, nsenales = e.shape

    if t.size != nmuestras:
        raise ValueError(
            "t debe tener un elemento por cada muestra de e."
        )

    if nmuestras < 2:
        raise ValueError("Se necesita al menos 2 muestras")

    if np.any(np.diff(t) <= 0):
        raise ValueError("Los tiempos deben ser estrictamente crecientes")

    et = np.sum(e**2, axis=1)

    t = t - t[0]

    y1F = 0.0
    y1Fk1 = 0.0 
    Tant = 0.0

    for k in range(nmuestras):
        Tf = t[k] - Tant
        Tant = t[k]

        y1F = Tf * et[k] + y1Fk1
        y1Fk1 = y1F

    T = t[-1] - t[0]

    nL2 = np.sqrt((1 / T) * y1F)

    return float(nL2)

def linea_punteada(po: float, pf: float, *, ax: Any = None) -> None:

    po = np.asarray(po, dtype=float).reshape(-1)
    pf = np.asarray(pf, dtype=float).reshape(-1)

    if po.size < 3 or pf.size < 3:
        raise ValueError("po y pf deben contener al menos 3 coordenadas")

    ax = _obtener_axes_3d(ax)

    ax.plot([po[0], pf[0]], [po[1], pf[1]], [po[2], pf[2]], linestyle="--", color = "black")

def Load_STL(archivo: str) -> Any:

    #Lee un archivo STL y devuelve una estructura con los datos geométricos del sólido.

    ruta = Path(archivo)

    if not ruta.is_file():
        raise ValueError(f"No se encuentra el archivo STL: {ruta}")

    malla = trimesh.load(
        str(ruta),
        file_type="stl",
        force="mesh",
        process=True
    )

    v = np.asarray(malla.vertices, dtype=float)
    f = np.asarray(malla.faces, dtype=np.int64)
    n = np.asarray(malla.face_normals, dtype=float)

    c = None

    stltitle = ruta.name

    solido = SimpleNamespace(vertices = v, faces = f, normals = n, colors = c, STLtitle = stltitle)

    return solido

def gripper(H: Any, L: float, lw: float, *, ax: Any = None) -> None:

    # Dibuja una pinza robótica mediante segmentos de línea.

    
    H = np.asarray(H, dtype=float)

    if H.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    P0 = H @ np.asarray([0, 0, 0, 1], dtype=float)
    P1 = H @ np.asarray([0, 0, L, 1], dtype=float)
    PL1 = H @ np.asarray([0, -L * 0.4, L, 1], dtype=float)
    PL2 = H @ np.asarray([0, -L * 0.4, L * 1.4, 1], dtype=float)
    PR1 = H @ np.asarray([0, L * 0.4, L, 1], dtype=float)
    PR2 = H @ np.asarray([0, L * 0.4, L * 1.4, 1], dtype=float)

    eslabon(P0,P1,'k',lw, ax = ax)
    eslabon(P1,PL1,'k',lw, ax = ax)
    eslabon(PL1,PL2,'k',lw, ax = ax)
    eslabon(P1,PR1,'k',lw, ax = ax)
    eslabon(PR1,PR2,'k',lw, ax = ax)

def giroZ(K: Any, theta_min_max: Any, r_a: Any, lth: str, lposXYZ: Any, tf: float, *, ax: Any = None) -> None:

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    theta = np.arange(theta_min_max[0], theta_min_max[1] + pi/360, pi/180 )

    x = r_a[0]*np.cos(theta)
    y = r_a[0]*np.sin(theta)

    z = np.full_like(theta, r_a[1])

    XYZ = K @ np.vstack((x, y, z, np.ones_like(theta)))

    ax.plot(XYZ[0, :], XYZ[1, :], XYZ[2, :], "k", linewidth = 2)

    ancho = r_a[0] / 8
    alto = r_a[0] / 4

    Kcono = K @ rotz(theta_min_max[1]) @ trans(r_a[0], 0, r_a[1]) @ rotx(-pi/2) @ trans(0, 0, -alto)

    cono(Kcono, alto, ancho, "gray", ax = ax)

    posletra = K @ [lposXYZ[0], lposXYZ[1], lposXYZ[2], 1]

    if lth != " ":
        ax.text(posletra[0], posletra[1], posletra[2], f"${lth}$", fontsize=tf)

def giro_z(K: Any, theta_max: Any, r: Any, lth: str, lpos: Any, tf: float, *, ax: Any = None) -> None:

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)

    theta = np.arange(0, theta_max + pi/360, pi/180 )

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    z = np.zeros_like(theta)

    XYZ = K @ np.vstack((x, y, z, z + 1))

    ax.plot(XYZ[0, :], XYZ[1, :], XYZ[2, :], color = "black", linewidth = 2)

    ancho = r / 8
    alto = r / 4

    Kcono = K @ rotz(theta_max) @ trans(r, 0, 0) @ rotx(-pi/2) @ trans(0, 0, -alto)

    cono(Kcono, alto, ancho, "gray", ax = ax)

    veces = 1.4
    posletra = K @ [veces * r * np.cos(lpos), veces * r * np.sin(lpos), 0, 1]

    if lth != " ":
        ax.text(posletra[0], posletra[1], posletra[2], f"${lth}$", fontsize=tf)

def eslabon_STL(H: Any, solido: Any, RGBcolor: Any, *, ax: Any = None) -> None:

    # Esta función se utiliza para dibujar un objeto sólido cargado apartir de 
    # un archivo STL en la pose indicada por la matriz de transformación H

    H = np.asarray(H, dtype=float)
    RGBcolor = np.asarray(RGBcolor, dtype=float)

    if H.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    if RGBcolor.shape != (3,):
        raise ValueError("RGBcolor debe contener tres valores RGB.")

    if np.any((RGBcolor < 0) | (RGBcolor > 1)):
        raise ValueError("Los componentes RGB deben estar entre 0 y 1.")

    vertices = np.asarray(solido.vertices, dtype=float)
    caras = np.asarray(solido.faces, dtype=np.int64)

    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("solido.vertices debe tener forma (n, 3)")

    if caras.ndim != 2 or caras.shape[1] != 3:
        raise ValueError("solido.faces debe tener forma (m, 3)")

    vn = H @ np.vstack((vertices.T, np.ones(vertices.shape[0])))

    vertices_transformados = vn[:3, :].T

    ax = _obtener_axes_3d(ax)

    triangulos = vertices_transformados[caras]

    luz = LightSource(azdeg=315, altdeg=45)

    colores = np.tile(RGBcolor, (caras.shape[0], 1))

    superficie = Poly3DCollection(triangulos, facecolors=colores, edgecolors=colores, linewidths=0, shade=True, lightsource=luz)

    ax.add_collection3d(superficie)

    ax.auto_scale_xyz(vertices_transformados[:, 0], vertices_transformados[:, 1], vertices_transformados[:, 2])

def esfera(K: Any, radio: float, color: str, *, ax: Any = None) -> None:

    # Esta función se utiliza para dibujar una esfera cuyo centro coincide con
    # el origen del sistema relacionado con la matriz de transformación K.

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    u = np.linspace(0, 2 * pi, 21)
    v = np.linspace(0, pi, 21)    

    U, V = np.meshgrid(u, v)

    Xs = np.cos(U) * np.sin(V)
    Ys = np.sin(U) * np.sin(V)
    Zs = np.cos(V)

    Xs = Xs * radio
    Ys = Ys * radio
    Zs = Zs * radio

    p = K @ np.array([0, 0, 0, 1], dtype=float)

    Xs = Xs + p[0]
    Ys = Ys + p[1]
    Zs = Zs + p[2]

    ax = _obtener_axes_3d(ax) 

    colores = {
        "red": (1, 0, 0),
        "green": (0, 1, 0),
        "blue": (0, 0, 1)
    }

    if color in colores:

        ax.plot_surface(Xs, Ys, Zs, color=colores[color], edgecolor="none", shade=False)

    else:
        ax.plot_surface(Xs, Ys, Zs, cmap="gray", edgecolor="none", shade=False)

def ejes3D(Po: Any, Px: Any, Py: Any, Pz: Any, cx: str, cy: str, cz: str, lw: float, *, ax: Any = None) -> None:

    po = np.asarray(Po, dtype=float).reshape(-1)
    px = np.asarray(Px, dtype=float).reshape(-1)
    py = np.asarray(Py, dtype=float).reshape(-1)
    pz = np.asarray(Pz, dtype=float).reshape(-1)


    if any(p.size < 3 for p in (po, px, py, pz)):
        raise ValueError("Cada punto debe contener al menos 3 coordenadas")

    ax = _obtener_axes_3d(ax)

    ax.plot([po[0], px[0]], [po[1], px[1]], [po[2], px[2]], color=cx, linewidth=lw)
    ax.plot([po[0], py[0]], [po[1], py[1]], [po[2], py[2]], color=cy, linewidth=lw)
    ax.plot([po[0], pz[0]], [po[1], pz[1]], [po[2], pz[2]], color=cz, linewidth=lw)

    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.set_zlabel("Eje Z")
    ax.grid(True)

def distancia_z(K: Any, altura: float, offsetXY: Any, ld: str, off_label: Any, tf: float, *, ax: Any = None) -> None:

    # Esta función se utiliza para dibujar una doble flecha paralela al eje Z 
    # correspondiente al sistema coordenado que ubica K con respecto al
    # origen. 

    K = np.asarray(K, dtype=float)
    offsetXY = np.asarray(offsetXY, dtype=float).reshape(-1)
    off_label = np.asarray(off_label, dtype=float).reshape(-1)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)
    
    po = K @ np.array([offsetXY[0], offsetXY[1], 0, 1], dtype=float)
    pf = K @ np.array([offsetXY[0], offsetXY[1], altura, 1], dtype=float)

    ax.plot([po[0], pf[0]], [po[1], pf[1]], [po[2], pf[2]], "k", linewidth=2)


    alto = altura * 0.08
    radio = altura * 0.03

    cono(K @ trans(offsetXY[0], offsetXY[1], altura - alto), alto, radio, "gray", ax = ax)
    cono(K @ trans(offsetXY[0], offsetXY[1], alto) @ rotx(pi), alto, radio, "gray", ax = ax)

    posletra = K @ np.array([off_label[0], off_label[1], off_label[2], 1], dtype    =float)

    if ld != " ":

        ax.text(posletra[0], posletra[1], posletra[2], f"${ld}$", fontsize=tf)

def DibujaPlano(LX: float, LY: float, K: Any, nalpha: float, *, ax: Any = None) -> None:

    # Esta función se utiliza para dibujar un plano cuyo origen está
    # relacionado con la matriz de transformación homogenea K.

    K = np.asarray(K, dtype=float)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    if not 0.0 <= nalpha <= 1.0:
        raise ValueError("nalpha debe estar entre 0 y 1")

    ax = _obtener_axes_3d(ax)

    Datos=np.array([
           [0, LX,  0, LX, LX/2],
           [0,  0, LY, LY, LX/2],
           [0,  0,  0,  0,    0],
           [1,  1,  1,  1,    1]], dtype=float)

    Datos2=np.array([
            [0, LX, LX,  0,  0],
            [0,  0, LY, LY,  0],
            [0,  0,  0,  0,  0],
            [1,  1,  1,  1,  1]], dtype=float)

    Plano = K @ Datos

    Contorno = K @ Datos2

    xx = Plano[0, :]
    yy = Plano[1, :]
    zz = Plano[2, :]

    ax.plot_trisurf(xx, yy, zz, color=(0, 0, 1), edgecolor="none", linewidth=0, shade=0, alpha=nalpha)

    ax.plot(Contorno[0, :], Contorno[1, :], Contorno[2, :], color="k")

def desplazamiento_z(K: Any, altura: float, offsetXY: Any, ld: str, off_label: Any, tf: float, *, ax: Any = None) -> None:

    # Esta función se utiliza para dibujar una flecha paralela al eje Z 
    # correspondiente al sistema coordenado que ubica K con respecto al origen.
    
    K = np.asarray(K, dtype=float)
    offsetXY = np.asarray(offsetXY, dtype=float).reshape(-1)
    off_label = np.asarray(off_label, dtype=float).reshape(-1)

    if K.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    ax = _obtener_axes_3d(ax)
    
    po = K @ np.array([offsetXY[0], offsetXY[1], 0, 1], dtype=float)
    pf = K @ np.array([offsetXY[0], offsetXY[1], altura, 1], dtype=float)

    ax.plot([po[0], pf[0]], [po[1], pf[1]], [po[2], pf[2]], "k", linewidth=2)


    alto = altura * 0.08
    radio = altura * 0.03

    cono(K @ trans(offsetXY[0], offsetXY[1], altura - alto), alto, radio, "gray", ax = ax)

    posletra = K @ np.array([off_label[0], off_label[1], off_label[2], 1], dtype    =float)

    if ld != " ":

        ax.text(posletra[0], posletra[1], posletra[2], f"${ld}$", fontsize=tf)


def Dibujar_intermedio(Tk1: float, Tk2: float, Tki: Any, nfig: int) -> None:

    Tk1 = np.asarray(Tk1, dtype=float)
    Tk2 = np.asarray(Tk2, dtype=float)
    Tki = np.asarray(Tki, dtype=float)

    if Tk1.shape != (4, 4) and Tk2.shape != (4, 4) and Tki.shape != (4, 4):
        raise ValueError("Tki debe ser una matriz de transformacion 4x4")

    H00 = np.eye(4)
    ini_fin = False

    tf = 14
    tt = 1

    fig = plt.figure(nfig)
    fig.clf()

    ax = fig.add_subplot(111, projection="3d")

    po0 = Sistema3D(H00, tt, "X_0", "y_0", "z_0", tf, ax=ax) 

    if ini_fin:

        pTk0 = Sistema3D(Tk1, tt, "x_i", "y_i", "z_i", tf, ax=ax)

        pTkF = Sistema3D(Tk2, tt, "x_f", "y_f", "z_f", tf, ax=ax)

    else: 

        origen = np.array([[0], [0], [0], [1]])

        pTk0 = Tk1 @ origen
        pTkF = Tk2 @ origen

    alto = tt * 0.6
    radio = tt * 0.2

    if ini_fin:

        prisma_rectangular(Tk1, radio, radio, alto, "yellow", ax=ax)

        prisma_rectangular(Tk2, radio, radio, alto, "yellow", ax=ax)

    prisma_rectangular(Tki, radio, radio, alto, "yellow", ax=ax)

    linea_punteada(pTk0, pTkF, ax=ax)

    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 3)
    ax.set_zlim(-1, 5)

    ax.set_box_aspect((6, 4, 6))
    ax.grid(True)

    ax.view_init(elev=50, azim=80)
    ax.set_proj_type("persp")

    ax.set_title("Interpolación")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    fig.tight_layout()

    return fig, ax
    