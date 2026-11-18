"""Casos de prueba compartidos.

Los usan:
  * tools/generar_referencias.py: ejecuta la toolbox .m original en Octave y guarda
    las salidas en tests/referencias/octave_ref.json.
  * tests/test_equivalencia_matlab.py: ejecuta SimpleRobotics con las mismas
    entradas y compara sus resultados contra el JSON de referencia.

Las entradas se construyen con NumPy y funciones auxiliares independientes de
SimpleRobotics, para que un cambio en la biblioteca bajo prueba no modifique
los datos de entrada.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np


class Fila:
    """Vector fila (1xN) en Octave. Para Python se adapta a un vector 1D."""

    def __init__(self, datos):
        self.a = np.asarray(datos, dtype=float).ravel()


@dataclass(frozen=True)
class Caso:
    id: str
    fn: str
    args: tuple
    nout: int = 1


# ----------------------------------------------------------------- conversiones

def a_python(x):
    """Argumento tal como se entrega actualmente a la función de Python."""
    return x.a if isinstance(x, Fila) else x


def a_json(x):
    """Convierte un argumento a tipos serializables por JSON."""
    return np.asarray(a_python(x), dtype=float).tolist()


def decodificar_numero_json(valor):
    """Recupera NaN e infinitos guardados como cadenas en el JSON de referencias."""
    especiales = {"NaN": np.nan, "Infinity": np.inf, "-Infinity": -np.inf}
    if isinstance(valor, str) and valor in especiales:
        return especiales[valor]
    return float(valor)


def a_octave(x) -> str:
    """Construye un literal de Octave; Fila se escribe como vector fila."""
    if isinstance(x, Fila):
        return "[" + ",".join(repr(float(v)) for v in x.a) + "]"

    a = np.asarray(x, dtype=float)
    if a.ndim == 0:
        return repr(float(a))
    if a.ndim == 1:  # Los arreglos 1D se envían como vectores columna.
        return "[" + ";".join(repr(float(v)) for v in a) + "]"
    return "[" + ";".join(",".join(repr(float(v)) for v in fila) for fila in a) + "]"


# ------------------------------------------------- ayudantes de rotación (NumPy puro)

def rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def rot_eje(k, th):
    """Fórmula de Rodrigues para un eje unitario."""
    k = unit(k)
    K = np.array(
        [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]],
        dtype=float,
    )
    return np.cos(th) * np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * np.outer(k, k)


def hom(R, t=(0.0, 0.0, 0.0)):
    H = np.eye(4)
    H[:3, :3] = R
    H[:3, 3] = t
    return H


def trans_h(x, y, z):
    return hom(np.eye(3), (x, y, z))


# ----------------------------------------------------------------------- casos
EJES = {
    "X": [1, 0, 0],
    "Y": [0, 1, 0],
    "Z": [0, 0, 1],
    "oblicuo_122": unit([1, 2, 2]),
    "oblicuo_1m22": unit([1, -2, 2]),
    "oblicuo_112": unit([1, 1, 2]),
    "oblicuo_m212": unit([-2, 1, 2]),
}
ANGULOS = {
    "0": 0.0,
    "1e-7": 1e-7,
    "0.5": 0.5,
    "1.0": 1.0,
    "2.0": 2.0,
    "3.0": 3.0,
    "pi_menos_1e-8": pi - 1e-8,
    "pi": pi,
}


def construir_casos() -> list[Caso]:
    rng = np.random.RandomState(0)  # No cambiar el orden de las llamadas a rng.
    ejes = {k: np.asarray(v, dtype=float) for k, v in EJES.items()}
    ejes["aleatorio"] = unit(rng.randn(3))

    C: list[Caso] = []

    # --- rotaciones y traslaciones elementales
    for etq, ang in {
        "0": 0.0,
        "0.3": 0.3,
        "m1.2": -1.2,
        "pi_2": pi / 2,
        "pi": pi,
        "2.5": 2.5,
    }.items():
        for ax in "xyz":
            C.append(Caso(f"rot{ax}3-{etq}", f"rot{ax}3", (ang,)))
            C.append(Caso(f"rot{ax}-{etq}", f"rot{ax}", (ang,)))

    C.append(Caso("trans-enteros", "trans", (1.0, 2.0, 3.0)))
    C.append(Caso("trans-decimales", "trans", (0.1, -0.2, 0.3)))
    C.append(Caso("Rot_RPY", "Rot_RPY", (0.3, 0.4, 0.5)))
    C.append(Caso("Rot_RPY_grados", "Rot_RPY_grados", (30.0, 40.0, 50.0)))

    # --- eje-ángulo
    for kn, k in ejes.items():
        C.append(Caso(f"Rot_eje-{kn}", "Rot_eje", (k, 0.7)))
        C.append(Caso(f"Rot_eje_grados-{kn}", "Rot_eje_grados", (k, 40.0)))
        for an, th in ANGULOS.items():
            H = hom(rot_eje(k, th), (0.1, 0.2, 0.3))
            C.append(Caso(f"Eje_theta-eje_{kn}-th_{an}", "Eje_theta", (H,), nout=2))

    Hg2 = hom(rot_eje(ejes["oblicuo_122"], 1.3))
    C.append(Caso("Eje_theta_grados", "Eje_theta_grados", (Hg2,), nout=2))

    # --- RPY
    configuraciones_rpy = {
        "general": (0.3, 0.4, 0.5),
        "general2": (-2.0, 1.0, 3.0),
        "cardan_mas90": (0.3, pi / 2, 0.5),
        "cardan_menos90": (0.3, -pi / 2, 0.5),
    }
    for nm, (a, b, c) in configuraciones_rpy.items():
        H = hom(rz(a) @ ry(b) @ rx(c))
        C.append(Caso(f"RPY-{nm}", "RPY", (H,), nout=3))
        C.append(Caso(f"RPY_grados-{nm}", "RPY_grados", (H,), nout=3))

    # --- inversa y cuaterniones
    Hg = trans_h(1, 2, 3) @ hom(rz(0.3) @ rx(0.7))
    C.append(Caso("H_inv", "H_inv", (Hg,)))

    for quat in [
        (0.9, 0.1, -0.3, 0.2),
        (0.5, 0.5, 0.5, 0.5),
        (2.0, 0.0, 0.0, 0.0),
    ]:
        C.append(Caso("Rot_Q-" + "_".join(f"{v:g}" for v in quat), "Rot_Q", quat))

    configuraciones_eje = {
        "general": (ejes["oblicuo_122"], 0.7),
        "th_2.5": (ejes["aleatorio"], 2.5),
        "180_X": (ejes["X"], pi),
        "180_Z": (ejes["Z"], pi),
    }
    for nm, (k, th) in configuraciones_eje.items():
        C.append(Caso(f"Quaternions-{nm}", "Quaternions", (hom(rot_eje(k, th)),), nout=4))
        C.append(Caso(f"Axis2Quaternions-{nm}", "Axis2Quaternions", (k, th), nout=4))

    # --- derivadas
    t11 = np.linspace(0, 2, 11)
    t101 = np.linspace(0, 2, 101)
    for fn in ("derivada_numerica", "derivada_numerica2", "derivada_numerica_central"):
        C.append(Caso(f"{fn}-n11", fn, (Fila(np.sin(t11)), Fila(t11))))
        C.append(Caso(f"{fn}-n101", fn, (Fila(np.sin(t101) ** 2), Fila(t101))))
        C.append(Caso(f"{fn}-2_muestras", fn, (Fila([0.0, 1.0]), Fila([0.0, 1.0]))))

    # --- interpolaciones
    C.append(Caso("interpolacion_lineal", "interpolacion_lineal", (1.0, 4.0, 0.0, 2.0, 0.5)))
    C.append(Caso("interpolacion_lineal_vector", "interpolacion_lineal_vector", (0.0, 3.0, Fila(t11)), nout=2))
    C.append(
        Caso(
            "interpolacion_lineal_vector-2_muestras",
            "interpolacion_lineal_vector",
            (0.0, 3.0, Fila([0.0, 1.0])),
            nout=2,
        )
    )

    casos_cubica = {
        "qp_cero_T10": (5.0, 50.0, 0.0, 0.0, 10.0),
        "qp_distinta_T2": (0.0, 1.0, 1.0, 2.0, 2.0),
        "qp_distinta_T1": (0.0, 1.0, 1.0, 2.0, 1.0),
    }
    for nm, (qi, qf, qpi, qpf, tf) in casos_cubica.items():
        C.append(
            Caso(
                f"interpolacion_cubica_vector-{nm}",
                "interpolacion_cubica_vector",
                (qi, qf, qpi, qpf, Fila(np.linspace(0, tf, 101))),
                nout=2,
            )
        )
        for j, tp in enumerate([0.0, tf / 3, tf]):
            C.append(
                Caso(
                    f"interpolacion_cubica-{nm}-t{j}",
                    "interpolacion_cubica",
                    (qi, qf, qpi, qpf, 0.0, tf, tp),
                )
            )

    casos_tramos = {
        "trapezoidal": (0.0, 5.0, 1.0, 1.0),
        "triangular": (0.0, 0.5, 1.0, 1.0),
        "negativo": (5.0, -3.0, 2.0, 4.0),
        "sin_desplazamiento": (2.0, 2.0, 1.0, 1.0),
    }
    for nm, (qi, qf, V, A) in casos_tramos.items():
        T = abs(qf - qi) / V + V / A
        tt = np.linspace(-0.5, T + 1.0, 31)  # Incluye t<0 y t>T intencionalmente.
        C.append(
            Caso(
                f"interpolacion_tramos_vector-{nm}",
                "interpolacion_tramos_vector",
                (qi, qf, V, A, Fila(tt)),
                nout=2,
            )
        )
        C.append(Caso(f"interpolacion_tramos-{nm}-t0.9", "interpolacion_tramos", (qi, qf, V, A, 0.9)))

    # --- energía, norma, ejes, DH
    qp, tau, e = rng.randn(5, 2), rng.randn(5, 2), rng.randn(5, 2)
    for nm, tt in {
        "t_desde_0": np.linspace(0, 2, 5),
        "t_desde_10": np.linspace(10, 12, 5),
    }.items():
        C.append(Caso(f"Energia_robot-{nm}", "Energia_robot", (qp, tau, Fila(tt))))
        C.append(Caso(f"normaL2-{nm}", "normaL2", (e, tt)))

    C.append(Caso("ejes", "ejes", (trans_h(1, 1, 1) @ hom(rz(0.5)), 0.8), nout=4))
    C.append(Caso("DH", "DH", (0.5, 0.2, 0.1, pi / 2)))

    ids = [caso.id for caso in C]
    assert len(ids) == len(set(ids)), "Hay identificadores de casos duplicados."
    return C


if __name__ == "__main__":
    casos = construir_casos()
    print(f"Casos definidos: {len(casos)}")
    print("Primeros cinco:")
    for caso in casos[:5]:
        print(f"  {caso.id}: {caso.fn}{caso.args} (salidas={caso.nout})")
