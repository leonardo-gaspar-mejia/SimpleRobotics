#!/usr/bin/env python3
"""Genera tests/referencias/octave_ref.json ejecutando
la toolbox .m original en GNU Octave.

Uso:
    python tools/generar_referencias.py "C:/ruta/Simple_Robotics_Toolbox_oct2026"

Requisito:
    octave-cli debe estar disponible en PATH.
    También se puede indicar mediante OCTAVE_CLI.

Este programa solo se necesita para crear o actualizar
el archivo de referencias.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from pathlib import Path
from typing import Any


RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "tests" / "referencias" / "octave_ref.json"


# ---------------------------------------------------------
# FUNCIÓN AUXILIAR DE OCTAVE
# ---------------------------------------------------------

EMIT_M = r"""function emit(fid, name, M)

  if ~(isnumeric(M) || islogical(M)) || ~isreal(M)
    error('emit:TipoNoSoportado', ...
          'La salida debe ser numérica, lógica o real.');
  end

  M = double(M);
  [r, c] = size(M);

  fprintf(fid, '%s %d %d', name, r, c);

  % Transponemos para escribir en orden por filas.
  Mt = M.';
  fprintf(fid, ' %.17g', Mt(:));

  fprintf(fid, '\n');

end
"""


# ---------------------------------------------------------
# PREPARACIÓN DE RUTAS
# ---------------------------------------------------------

def q(ruta: Path) -> str:
    """Prepara una ruta para introducirla en Octave."""

    return str(ruta).replace("\\", "/").replace("'", "''")


def buscar_octave() -> str:
    """Encuentra octave-cli en PATH o mediante OCTAVE_CLI."""

    configurado = os.environ.get("OCTAVE_CLI")

    if configurado:

        ruta_configurada = Path(configurado).expanduser()

        if ruta_configurada.is_file():
            return str(ruta_configurada.resolve())

        encontrado = shutil.which(configurado)

        if encontrado:
            return encontrado

        sys.exit(
            "OCTAVE_CLI está configurado, "
            f"pero no encuentro el ejecutable: {configurado}"
        )

    ejecutable = (
        shutil.which("octave-cli")
        or shutil.which("octave-cli.exe")
    )

    if ejecutable is None:

        sys.exit(
            "No encuentro octave-cli en PATH. "
            "Agrega la carpeta bin de GNU Octave al PATH "
            "o define OCTAVE_CLI con la ruta completa "
            "de octave-cli.exe. "
            "Comprueba la instalación con: "
            "octave-cli --version"
        )

    return ejecutable


# ---------------------------------------------------------
# CONVERSIÓN DE RESULTADOS A JSON
# ---------------------------------------------------------

def numero_para_json(valor: float) -> float | str:
    """Codifica NaN e infinitos como cadenas."""

    if math.isnan(valor):
        return "NaN"

    if math.isinf(valor):
        return "Infinity" if valor > 0 else "-Infinity"

    return valor


# ---------------------------------------------------------
# LECTURA DE RESULTADOS DE OCTAVE
# ---------------------------------------------------------

def leer_salida(path: Path) -> dict[str, tuple[Any, ...]]:
    """Lee los registros escritos por emit()."""

    crudo: dict[str, tuple[Any, ...]] = {}

    for linea in path.read_text(encoding="utf-8").splitlines():

        if not linea.strip():
            continue

        partes = linea.split(maxsplit=3)

        # -----------------------------------------
        # Registro de error
        # -----------------------------------------

        if len(partes) >= 2 and partes[1] == "ERROR":

            nombre = partes[0]

            mensaje = (
                " ".join(partes[2:])
                if len(partes) >= 3
                else "Error sin mensaje"
            )

            crudo[nombre] = ("ERROR", mensaje)
            continue

        # -----------------------------------------
        # Registro numérico
        # -----------------------------------------

        if len(partes) < 3:

            raise RuntimeError(
                f"Registro incompleto escrito por Octave: {linea!r}"
            )

        nombre = partes[0]

        try:

            filas = int(partes[1])
            columnas = int(partes[2])

            datos_texto = (
                partes[3].split()
                if len(partes) == 4
                else []
            )

            datos = [float(x) for x in datos_texto]

        except ValueError as exc:

            raise RuntimeError(
                f"No pude interpretar el registro: {linea!r}"
            ) from exc

        if filas < 0 or columnas < 0:

            raise RuntimeError(
                f"El registro {nombre} contiene dimensiones negativas."
            )

        if len(datos) != filas * columnas:

            raise RuntimeError(
                f"El registro {nombre} declara "
                f"{filas}x{columnas}, "
                f"pero contiene {len(datos)} valores."
            )

        crudo[nombre] = (
            "OK",
            [filas, columnas],
            datos
        )

    return crudo


# ---------------------------------------------------------
# GENERACIÓN DEL SCRIPT DE OCTAVE
# ---------------------------------------------------------

def construir_script(
    casos: list[Any],
    toolbox_dir: Path,
    tmp: Path,
    salida_txt: Path,
    convertir_argumento: Any,
) -> str:

    """Construye el archivo .m que ejecutará Octave."""

    lineas = [

        "more off;",

        f"addpath('{q(toolbox_dir)}');",

        f"addpath('{q(tmp)}');",

        f"fid = fopen('{q(salida_txt)}', 'w');",

        "if fid < 0, "
        "error('No se pudo abrir el archivo de resultados'); "
        "end",

    ]

    for i, caso in enumerate(casos):

        # -----------------------------------------
        # Convertir argumentos Python a Octave
        # -----------------------------------------

        argumentos = ",".join(
            convertir_argumento(arg)
            for arg in caso.args
        )

        # -----------------------------------------
        # Preparar variables de salida
        # -----------------------------------------

        nombres_salida = [
            f"o{j}"
            for j in range(1, caso.nout + 1)
        ]

        lhs = (
            nombres_salida[0]
            if caso.nout == 1
            else "[" + ",".join(nombres_salida) + "]"
        )

        # -----------------------------------------
        # Preparar escritura de resultados
        # -----------------------------------------

        emisiones = " ".join(

            f"emit(fid, 'c{i}#{j}', o{j});"

            for j in range(1, caso.nout + 1)

        )

        # -----------------------------------------
        # Preparar registro de errores
        # -----------------------------------------

        registros_error = " ".join(

            f"fprintf(fid, 'c{i}#{j} ERROR %s\\n', msg);"

            for j in range(1, caso.nout + 1)

        )

        # -----------------------------------------
        # Construir instrucción completa
        # -----------------------------------------

        linea = (

            f"try, {lhs} = {caso.fn}({argumentos}); "

            f"{emisiones} "

            "catch err, "

            "msg = strrep(err.message, sprintf('\\n'), ' '); "

            f"{registros_error} "

            "end"

        )

        lineas.append(linea)

    lineas.append("fclose(fid);")

    return "\n".join(lineas) + "\n"


# ---------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------

def main(toolbox: str) -> None:

    octave = buscar_octave()

    toolbox_dir = Path(toolbox).expanduser().resolve()

    # -----------------------------------------
    # Verificar toolbox
    # -----------------------------------------

    archivo_prueba = toolbox_dir / "Eje_theta.m"

    if not archivo_prueba.is_file():

        sys.exit(
            f"No encuentro Eje_theta.m en {toolbox_dir}. "
            "Pasa la carpeta raíz de la toolbox original."
        )

    # -----------------------------------------
    # Importar casos de prueba
    # -----------------------------------------

    sys.path.insert(0, str(RAIZ / "tests"))

    try:

        from casos import (
            a_json,
            a_octave,
            construir_casos
        )

    except ImportError as exc:

        sys.exit(
            f"No pude importar tests/casos.py: {exc}"
        )

    casos = construir_casos()

    # -----------------------------------------
    # Crear entorno temporal
    # -----------------------------------------

    with tempfile.TemporaryDirectory(
        prefix="simplerobotics_octave_"
    ) as temporal:

        tmp = Path(temporal)

        salida_txt = tmp / "salida.txt"

        script = tmp / "ejecutar_casos.m"

        # -----------------------------------------
        # Crear función emit.m
        # -----------------------------------------

        emit_file = tmp / "emit.m"

        emit_file.write_text(
            EMIT_M,
            encoding="utf-8"
        )

        # -----------------------------------------
        # Crear script de Octave
        # -----------------------------------------

        script.write_text(

            construir_script(
                casos,
                toolbox_dir,
                tmp,
                salida_txt,
                a_octave
            ),

            encoding="utf-8"

        )

        # -----------------------------------------
        # Ejecutar Octave
        # -----------------------------------------

        try:

            ejecucion = subprocess.run(

                [
                    octave,
                    "--no-gui",
                    "--quiet",
                    str(script)
                ],

                capture_output=True,
                text=True,
                timeout=900,
                check=False

            )

        except subprocess.TimeoutExpired:

            sys.exit(
                "Octave superó el límite de 900 segundos."
            )

        except OSError as exc:

            sys.exit(
                f"No pude iniciar Octave ({octave}): {exc}"
            )

        # -----------------------------------------
        # Verificar ejecución
        # -----------------------------------------

        if ejecucion.returncode != 0:

            sys.exit(

                "Octave terminó con un error.\n"

                f"Código de salida: {ejecucion.returncode}\n"

                f"STDERR:\n{ejecucion.stderr[-4000:]}\n"

                f"STDOUT:\n{ejecucion.stdout[-2000:]}"

            )

        if not salida_txt.is_file():

            sys.exit(
                "Octave terminó, pero no generó "
                "el archivo de resultados."
            )

        # -----------------------------------------
        # Obtener versión de Octave
        # -----------------------------------------

        try:

            version = subprocess.run(

                [
                    octave,
                    "--version"
                ],

                capture_output=True,
                text=True,
                timeout=30,
                check=True

            ).stdout.splitlines()[0]

        except (
            subprocess.SubprocessError,
            OSError,
            IndexError
        ) as exc:

            version = f"No se pudo determinar ({exc})"

        # -----------------------------------------
        # Leer resultados
        # -----------------------------------------

        crudo = leer_salida(salida_txt)

    # -----------------------------------------------------
    # CONSTRUIR ARCHIVO JSON
    # -----------------------------------------------------

    resultado: dict[str, Any] = {

        "meta": {

            "generado": dt.datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),

            "motor": version,

            "origen_codigo": (
                "Archivos .m de la toolbox original "
                "ejecutados en GNU Octave"
            ),

            "toolbox": toolbox_dir.name,

            "correcciones_locales": [
                "DH.m: se corrigió transl por trans "
                "debido a un error tipográfico."
            ],

        },

        "casos": {}

    }

    # -----------------------------------------------------
    # PROCESAR RESULTADOS
    # -----------------------------------------------------

    casos_con_error = 0

    salidas_con_error = 0

    for i, caso in enumerate(casos):

        entrada: dict[str, Any] = {

            "fn": caso.fn,

            "entradas": [
                a_json(arg)
                for arg in caso.args
            ],

            "error": None,

            "salidas": []

        }

        errores_caso: list[str] = []

        for j in range(1, caso.nout + 1):

            clave = f"c{i}#{j}"

            registro = crudo.get(clave)

            # -------------------------------------
            # Salida ausente
            # -------------------------------------

            if registro is None:

                errores_caso.append(
                    f"Sin registro para la salida {j}"
                )

                salidas_con_error += 1

            # -------------------------------------
            # Salida con error
            # -------------------------------------

            elif registro[0] == "ERROR":

                errores_caso.append(
                    f"Salida {j}: {registro[1]}"
                )

                salidas_con_error += 1

            # -------------------------------------
            # Salida correcta
            # -------------------------------------

            else:

                _, forma, datos = registro

                entrada["salidas"].append({

                    "forma": forma,

                    "datos": [
                        numero_para_json(x)
                        for x in datos
                    ]

                })

        if errores_caso:

            entrada["error"] = "; ".join(errores_caso)

            casos_con_error += 1

        resultado["casos"][caso.id] = entrada

    # -----------------------------------------------------
    # GUARDAR REFERENCIAS
    # -----------------------------------------------------

    SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    SALIDA.write_text(

        json.dumps(

            resultado,

            indent=2,

            ensure_ascii=False,

            allow_nan=False

        ) + "\n",

        encoding="utf-8"

    )

    # -----------------------------------------------------
    # INFORME FINAL
    # -----------------------------------------------------

    print(
        f"Casos generados: {len(casos)}"
    )

    print(
        f"Casos con al menos una salida fallida: "
        f"{casos_con_error}"
    )

    print(
        f"Salidas fallidas o ausentes: "
        f"{salidas_con_error}"
    )

    print(
        f"Referencia guardada en: {SALIDA}"
    )

    print(
        f"Motor utilizado: {version}"
    )


if __name__ == "__main__":

    if len(sys.argv) != 2:

        sys.exit(__doc__)

    main(sys.argv[1])