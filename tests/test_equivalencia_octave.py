"""Compara SimpleRobotics con referencias generadas desde la toolbox .m en Octave.

Ejecutar desde la raíz del repositorio:
    python -m pytest -v

No requiere Octave: lee tests/referencias/octave_ref.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
REFERENCIA = RAIZ / "tests" / "referencias" / "octave_ref.json"

# Permite importar casos.py sin convertir tests/ en un paquete Python.
sys.path.insert(0, str(RAIZ / "tests"))
from casos import a_python, construir_casos, decodificar_numero_json  # noqa: E402

# Este nombre supone que el paquete/módulo principal se importa como:
#     import SimpleRobotics
# Si tu proyecto utiliza otro nombre de importación, cambia únicamente esta línea.
sys.path.insert(0, str(RAIZ))
try:
    import SimpleRobotics as sr  # type: ignore[import-not-found]  # noqa: E402
except ImportError as exc:  # pragma: no cover - el mensaje ayuda al usuario al configurar el proyecto
    raise ImportError(
        "No se pudo importar SimpleRobotics. Ejecuta pytest desde la raíz del repositorio "
        "y verifica que el módulo/paquete se llame SimpleRobotics y esté en esa carpeta. "
        "Si su nombre de importación es distinto, modifica el import de este archivo."
    ) from exc

CASOS = construir_casos()
RTOL = float(os.environ.get("SIMPLEROBOTICS_RTOL", "1e-7"))
ATOL = float(os.environ.get("SIMPLEROBOTICS_ATOL", "1e-9"))


@pytest.fixture(scope="session")
def datos_referencia() -> dict[str, Any]:
    """Carga una sola vez el JSON creado previamente por generar_referencias.py."""
    if not REFERENCIA.is_file():
        pytest.fail(
            f"No existe {REFERENCIA}. Primero genera las referencias con Octave: "
            "python tools/generar_referencias.py RUTA/A/LA/TOOLBOX"
        )

    try:
        datos = json.loads(REFERENCIA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        pytest.fail(f"No se pudo leer el JSON de referencias: {exc}")

    if "casos" not in datos or "meta" not in datos:
        pytest.fail("El JSON no tiene las secciones esperadas: 'meta' y 'casos'.")

    return datos


def _decodificar_matriz(salida: dict[str, Any]) -> np.ndarray:
    """Reconstruye la matriz usando dimensiones y datos guardados en el JSON."""
    forma = tuple(int(x) for x in salida["forma"])
    valores = [decodificar_numero_json(x) for x in salida["datos"]]
    if len(valores) != int(np.prod(forma)):
        raise AssertionError(
            f"La referencia declara forma {forma}, pero contiene {len(valores)} valores."
        )
    return np.asarray(valores, dtype=float).reshape(forma)


def _como_array(valor: Any, nombre: str) -> np.ndarray:
    """Convierte una salida numérica de SimpleRobotics en un ndarray real."""
    try:
        resultado = np.asarray(valor, dtype=float)
    except (TypeError, ValueError) as exc:
        raise AssertionError(
            f"La salida {nombre} no se puede convertir a un arreglo numérico real: {exc}"
        ) from exc
    return resultado


def _son_formas_vectoriales(forma: tuple[int, ...]) -> bool:
    """Acepta 1D de NumPy como equivalente práctico de 1xN o Nx1 de MATLAB."""
    if len(forma) <= 1:
        return True
    return len(forma) == 2 and 1 in forma


def _comparar_salida(actual: Any, esperada: np.ndarray, etiqueta: str) -> None:
    obtenido = _como_array(actual, etiqueta)

    # Un escalar de Python/NumPy equivale a la matriz 1x1 que entrega MATLAB/Octave.
    if obtenido.ndim == 0 and esperada.shape == (1, 1):
        obtenido = obtenido.reshape(1, 1)

    # NumPy suele representar vectores como (N,), mientras que Octave los registra
    # como (1,N) o (N,1). Se compara su contenido sin confundir matrices 2D generales.
    if obtenido.shape != esperada.shape:
        if (
            obtenido.size == esperada.size
            and _son_formas_vectoriales(obtenido.shape)
            and _son_formas_vectoriales(esperada.shape)
        ):
            obtenido = obtenido.reshape(-1)
            esperada = esperada.reshape(-1)
        else:
            raise AssertionError(
                f"{etiqueta}: dimensiones diferentes. "
                f"Python={obtenido.shape}; referencia Octave={esperada.shape}."
            )

    np.testing.assert_allclose(
        obtenido,
        esperada,
        rtol=RTOL,
        atol=ATOL,
        equal_nan=True,
        err_msg=(
            f"{etiqueta}: los valores difieren. "
            f"Tolerancias: rtol={RTOL}, atol={ATOL}."
        ),
    )


def test_el_json_contiene_todos_los_casos(datos_referencia: dict[str, Any]) -> None:
    """Detecta si el archivo de referencias y casos.py quedaron desincronizados."""
    ids_esperados = {caso.id for caso in CASOS}
    ids_guardados = set(datos_referencia["casos"])

    faltantes = sorted(ids_esperados - ids_guardados)
    sobrantes = sorted(ids_guardados - ids_esperados)
    assert not faltantes and not sobrantes, (
        f"Los casos y el JSON no coinciden. Faltan en JSON: {faltantes}. "
        f"Sobran en JSON: {sobrantes}."
    )


def test_referencias_identifican_octave(datos_referencia: dict[str, Any]) -> None:
    """Evita etiquetar accidentalmente una ejecución de Octave como MATLAB real."""
    motor = str(datos_referencia["meta"].get("motor", ""))
    origen = str(datos_referencia["meta"].get("origen_codigo", ""))
    assert "Octave" in motor or "Octave" in origen, (
        "El JSON no indica claramente que las referencias fueron generadas con GNU Octave."
    )


@pytest.mark.parametrize("caso", CASOS, ids=lambda caso: caso.id)
def test_equivalencia_caso(caso, datos_referencia: dict[str, Any]) -> None:
    """Ejecuta una función Python y compara cada salida con su referencia Octave."""
    referencia = datos_referencia["casos"][caso.id]

    # Un caso donde Octave no produjo resultado numérico no puede participar todavía
    # en una comparación de valores. Se reporta como SKIPPED, no como aprobado.
    if referencia.get("error"):
        pytest.skip(f"Octave no produjo todas las salidas: {referencia['error']}")

    funcion = getattr(sr, caso.fn, None)
    assert callable(funcion), (
        f"SimpleRobotics no expone una función invocable llamada {caso.fn!r}. "
        "Comprueba su nombre o el archivo __init__.py."
    )

    argumentos = tuple(a_python(arg) for arg in caso.args)
    try:
        resultado = funcion(*argumentos)
    except Exception as exc:
        pytest.fail(
            f"El caso {caso.id!r} lanzó {type(exc).__name__}: {exc}",
            pytrace=True,
        )

    if caso.nout == 1:
        resultados = [resultado]
    else:
        assert isinstance(resultado, (tuple, list)), (
            f"{caso.id}: se esperaban {caso.nout} salidas (tupla/lista), "
            f"pero Python devolvió {type(resultado).__name__}."
        )
        assert len(resultado) == caso.nout, (
            f"{caso.id}: se esperaban {caso.nout} salidas, "
            f"pero Python devolvió {len(resultado)}."
        )
        resultados = list(resultado)

    referencias_salidas = referencia.get("salidas", [])
    assert len(referencias_salidas) == caso.nout, (
        f"{caso.id}: el JSON contiene {len(referencias_salidas)} salidas; "
        f"se esperaban {caso.nout}."
    )

    for indice, (obtenida, salida_ref) in enumerate(
        zip(resultados, referencias_salidas), start=1
    ):
        esperada = _decodificar_matriz(salida_ref)
        _comparar_salida(obtenida, esperada, f"{caso.id}, salida {indice}")
