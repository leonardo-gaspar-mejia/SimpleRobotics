"""Funciones de presentación para matrices numéricas y simbólicas.

Estas funciones afectan únicamente a la visualización: la matriz original no se
modifica y conserva su tipo para poder seguir realizando operaciones.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def matriz_a_texto(matriz: Any, *, precision: int = 4) -> str:
    """Devuelve una representación legible de una matriz 2D.

    Las matrices de SymPy se formatean como una matriz matemática alineada.
    Las matrices numéricas se presentan con NumPy y precisión configurable.

    Args:
        matriz: Matriz simbólica de SymPy o matriz numérica convertible a ndarray.
        precision: Número de decimales para matrices numéricas.

    Returns:
        Texto formateado. La matriz original no se modifica.

    Raises:
        ValueError: Si la entrada no es bidimensional o precision es negativa.
        TypeError: Si la entrada no se puede interpretar como matriz.
    """
    if precision < 0:
        raise ValueError("precision debe ser mayor o igual que cero")

    modulo = type(matriz).__module__.split(".", 1)[0]
    if modulo == "sympy":
        try:
            import sympy as sp
        except ImportError as exc:  # pragma: no cover - objeto SymPy requiere el paquete
            raise ImportError("Instala SymPy para mostrar matrices simbólicas.") from exc

        if isinstance(matriz, sp.MatrixBase):
            return sp.pretty(matriz, use_unicode=True)

    try:
        arreglo = np.asarray(matriz)
    except (TypeError, ValueError) as exc:
        raise TypeError("matriz debe ser una matriz numérica o una matriz de SymPy") from exc

    if arreglo.ndim != 2:
        raise ValueError("matriz debe ser bidimensional")

    return np.array2string(
        arreglo,
        precision=precision,
        suppress_small=True,
        separator=" ",
    )


def mostrar_matriz(matriz: Any, *, precision: int = 4) -> None:
    """Imprime una matriz con formato legible, sin alterar la matriz original."""
    print(matriz_a_texto(matriz, precision=precision))


__all__ = ["matriz_a_texto", "mostrar_matriz"]
