from pathlib import Path

import numpy as np
import trimesh

from SimpleRobotics.transforms import rotz, trans
from SimpleRobotics.animation import RobotScene


# Dimensiones del robot, en metros.
L1 = 0.200
L2 = 0.150
D1 = 0.015
D2 = 0.010


def _cargar_stl(ruta: Path) -> trimesh.Trimesh:
    """Carga una geometría STL del robot."""
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encuentra el archivo STL: {ruta}")

    malla = trimesh.load(
        str(ruta),
        file_type="stl",
        force="mesh",
        process=True,
    )

    if not isinstance(malla, trimesh.Trimesh):
        raise TypeError(
            f"El archivo {ruta.name!r} no produjo una malla trimesh.Trimesh."
        )

    return malla


def _matrices_robot_rr(
    theta1: float,
    theta2: float,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Calcula las transformaciones de los elementos del robot RR."""
    H01 = np.asarray(rotz(theta1) @ trans(L1, 0, 0), dtype=float)
    H12 = np.asarray(rotz(theta2) @ trans(L2, 0, 0), dtype=float)
    H02 = H01 @ H12

    # Transformaciones usadas para ubicar los STL según el modelo MATLAB.
    HB = np.eye(4, dtype=float)
    HL1 = np.asarray(rotz(theta1) @ trans(0, 0, D1), dtype=float)
    HL2 = HL1 @ np.asarray(trans(L1, 0, 0), dtype=float) @ np.asarray(
        rotz(theta2), dtype=float
    )
    HL3 = HL2 @ np.asarray(trans(L2, 0, -D1 + D2), dtype=float)

    # La jerarquía de RobotScene requiere transformaciones locales.
    transformaciones_locales = {
        "base": HB,
        "link1": HL1,
        "link2": np.linalg.solve(HL1, HL2),
        "actuator": np.linalg.solve(HL2, HL3),
    }

    return transformaciones_locales, H02


def actualizar_pose_robot_rr(
    scene: RobotScene,
    theta1: float,
    theta2: float,
) -> np.ndarray:
    """Actualiza la pose del robot RR y devuelve H02."""
    locales, H02 = _matrices_robot_rr(theta1, theta2)

    scene.update_transforms(
        {
            "link1": locales["link1"],
            "link2": locales["link2"],
            "actuator": locales["actuator"],
        },
        space="local",
    )

    return H02


def Renderiza_Robot_RR(
    theta1: float,
    theta2: float,
    carpeta_stl: str | Path,
    *,
    mostrar: bool = True,
    mostrar_link2: bool = False,
    window_size: tuple[int, int] = (1000, 750),
) -> tuple[RobotScene, np.ndarray]:
    """Construye la escena 3D del robot RR a partir de sus archivos STL."""
    carpeta = Path(carpeta_stl).expanduser().resolve()

    archivos = {
        "Base": "Robot_2gdl_planar-Base.STL",
        "Link1": "Robot_2gdl_planar-Eslabon1.STL",
        "Link2": "Robot_2gdl_planar-Eslabon2.STL",
        "Actuador": "Robot_2gdl_planar-Actuador.STL",
    }

    mallas = {
        nombre: _cargar_stl(carpeta / archivo)
        for nombre, archivo in archivos.items()
    }

    locales, H02 = _matrices_robot_rr(theta1, theta2)

    scene = RobotScene(
        window_size=window_size,
        background="white",
        axes=True,
        grid=True,
    )

    scene.add_frame("base", transform=locales["base"])
    scene.add_frame("link1", parent="base", transform=locales["link1"])
    scene.add_frame("link2", parent="link1", transform=locales["link2"])
    scene.add_frame(
        "actuator",
        parent="link2",
        transform=locales["actuator"],
    )

    # Colores equivalentes a los RGB del ejemplo MATLAB.
    scene.add_mesh(
        "Base", mallas["Base"], frame="base", color=(1.0, 1.0, 0.0)
    )
    scene.add_mesh(
        "Link1", mallas["Link1"], frame="link1", color=(1.0, 0.6, 0.0)
    )

    # MATLAB calcula HL2 y carga Link2, pero no dibuja ese STL.
    if mostrar_link2:
        scene.add_mesh(
            "Link2", mallas["Link2"], frame="link2", color="lightgray"
        )

    scene.add_mesh(
        "Actuador",
        mallas["Actuador"],
        frame="actuator",
        color=(1.0, 0.8, 0.8),
    )

    scene.plotter.show_bounds(
        bounds=(-0.4, 0.4, -0.4, 0.4, -0.01, 0.15),
        location="outer",
    )

    if mostrar:
        scene.show()

    return scene, H02
