"""Escenas 3D para animaciones de SimpleRobotics.

Este modulo contiene la primera pieza del sistema de animacion: RobotScene.
No implementa todavia el temporizador ni la reproduccion; eso correspondera
posteriormente a AnimationController.

Dependencias opcionales:
    pip install trimesh pyvista

Uso previsto:
    from SimpleRobotics.animation import RobotScene
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np


class RobotScene:
    """Administra frames, geometria y actores de una escena robotica 3D.

    Trimesh conserva el grafo de transformaciones. PyVista representa las
    mallas mediante actores. Cada malla se almacena en coordenadas locales y
    su actor recibe la transformacion global calculada por Trimesh.

    Parameters
    ----------
    window_size:
        Tamano inicial de la ventana (ancho, alto), en pixeles.
    background:
        Color de fondo aceptado por PyVista.
    axes:
        Si es True, muestra el widget de ejes de PyVista.
    grid:
        Si es True, muestra la cuadricula y los limites de referencia.
    base_frame:
        Nombre del sistema de referencia raiz. Por defecto, ``"world"``.

    Notes
    -----
    Las transformaciones pasadas a add_frame, add_mesh y set_transform son
    matrices homogeneas 4x4 que expresan la pose local respecto al padre.
    update_transforms tambien admite matrices globales usando space="world".
    """

    _MESH_NODE_PREFIX = "__mesh__:"

    def __init__(
        self,
        window_size: tuple[int, int] = (1000, 750),
        background: str = "white",
        axes: bool = True,
        grid: bool = True,
        base_frame: str = "world",
    ) -> None:
        # Importar dentro del constructor mantiene las dependencias de
        # visualizacion fuera de las importaciones matematicas principales.
        try:
            import pyvista as pv
            import trimesh
        except ImportError as exc:
            raise ImportError(
                "RobotScene requiere las dependencias de visualizacion. "
                "Instalalas con: pip install pyvista trimesh"
            ) from exc

        if (
            not isinstance(window_size, (tuple, list))
            or len(window_size) != 2
            or any(not isinstance(v, (int, np.integer)) or v <= 0 for v in window_size)
        ):
            raise ValueError("window_size debe contener dos enteros positivos.")

        self._pv = pv
        self._trimesh = trimesh
        self._base_frame = self._validar_nombre(base_frame, "base_frame")

        self._scene = trimesh.Scene(base_frame=self._base_frame)
        self._plotter = pv.Plotter(window_size=tuple(window_size))
        self._plotter.set_background(background)

        if axes:
            self._plotter.add_axes()
        if grid:
            self._plotter.show_grid()

        # Mapa de frames logicos y sus respectivos padres.
        self._frames: dict[str, str | None] = {self._base_frame: None}

        # Mapa entre nombres publicos de mallas y nodos internos de Trimesh.
        self._mesh_nodes: dict[str, str] = {}

        # Actores PyVista asociados a cada malla publica.
        self._actors: dict[str, Any] = {}

        self._closed = False

    # ------------------------------------------------------------------
    # Validacion y conversion interna
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_nombre(name: str, parametro: str = "name") -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{parametro} debe ser una cadena no vacia.")
        return name

    @staticmethod
    def _validar_matriz(matrix: Any, parametro: str = "matrix") -> np.ndarray:
        """Valida una transformacion afin homogenea 4x4 numerica."""
        try:
            result = np.asarray(matrix, dtype=float)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{parametro} debe ser una matriz numerica 4x4.") from exc

        if result.shape != (4, 4):
            raise ValueError(f"{parametro} debe tener dimensiones 4x4.")

        if not np.all(np.isfinite(result)):
            raise ValueError(f"{parametro} no puede contener NaN o infinitos.")

        if not np.allclose(result[3], [0.0, 0.0, 0.0, 1.0]):
            raise ValueError(
                f"La ultima fila de {parametro} debe ser [0, 0, 0, 1]."
            )

        return result.copy()

    @staticmethod
    def _a_polydata(mesh: Any, pv: Any) -> Any:
        """Convierte una malla triangular Trimesh a pyvista.PolyData."""
        vertices = np.asarray(mesh.vertices, dtype=float)
        faces = np.asarray(mesh.faces, dtype=np.int64)

        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("La geometria debe tener vertices con forma (N, 3).")

        if faces.ndim != 2 or faces.shape[1] != 3:
            raise ValueError("La geometria debe contener caras triangulares (M, 3).")

        if vertices.size == 0 or faces.size == 0:
            raise ValueError("No se pueden agregar mallas vacias a RobotScene.")

        # Formato VTK/PyVista: [3, i, j, k, 3, i, j, k, ...].
        faces_pv = np.column_stack(
            (np.full(len(faces), 3, dtype=np.int64), faces)
        ).ravel()

        return pv.PolyData(vertices, faces_pv)

    def _comprobar_abierta(self) -> None:
        if self._closed:
            raise RuntimeError("La escena ya fue cerrada y no puede modificarse.")

    def _nodo_de(self, name: str) -> str:
        """Devuelve el nombre interno del nodo asociado a un frame o malla."""
        if name in self._frames:
            return name
        if name in self._mesh_nodes:
            return self._mesh_nodes[name]
        raise KeyError(f"No existe un frame ni una malla llamada {name!r}.")

    def _sincronizar_actores(self) -> None:
        """Copia a cada actor la pose global actual de su nodo Trimesh."""
        for mesh_name, actor in self._actors.items():
            node_name = self._mesh_nodes[mesh_name]
            matrix_world, _ = self._scene.graph.get(
                node_name, self._base_frame
            )
            actor.user_matrix = matrix_world

    # ------------------------------------------------------------------
    # API publica: frames
    # ------------------------------------------------------------------

    def add_frame(
        self,
        name: str,
        parent: str | None = None,
        transform: Any | None = None,
    ) -> None:
        """Agrega un sistema de referencia hijo de ``parent``.

        ``transform`` es la matriz local del nuevo frame respecto a su padre.
        Si se omite, se utiliza la identidad.
        """
        self._comprobar_abierta()
        name = self._validar_nombre(name)
        parent = self._base_frame if parent is None else self._validar_nombre(parent, "parent")

        if name == self._base_frame:
            raise ValueError("No se puede volver a agregar el frame raiz.")
        if name.startswith(self._MESH_NODE_PREFIX):
            raise ValueError(
                f"Los nombres de frames no pueden comenzar con "
                f"{self._MESH_NODE_PREFIX!r}."
            )
        if name in self._frames or name in self._mesh_nodes:
            raise ValueError(f"Ya existe un frame o malla llamado {name!r}.")
        if parent not in self._frames:
            raise KeyError(f"No existe el frame padre {parent!r}.")

        matrix = self._validar_matriz(
            np.eye(4) if transform is None else transform,
            "transform",
        )

        self._scene.graph.update(
            frame_to=name,
            frame_from=parent,
            matrix=matrix,
        )
        self._frames[name] = parent

    # ------------------------------------------------------------------
    # API publica: geometria
    # ------------------------------------------------------------------

    def add_mesh(
        self,
        name: str,
        mesh: Any,
        frame: str,
        transform: Any | None = None,
        color: Any = "lightgray",
        opacity: float = 1.0,
        smooth_shading: bool = True,
    ) -> Any:
        """Asocia una malla Trimesh a un frame y crea su actor PyVista.

        La geometria se mantiene en coordenadas locales. ``transform`` ubica
        la malla respecto al frame indicado y puede omitirse para usar I4.
        Devuelve el actor creado por PyVista.
        """
        self._comprobar_abierta()
        name = self._validar_nombre(name)
        frame = self._validar_nombre(frame, "frame")

        if name in self._mesh_nodes or name in self._frames:
            raise ValueError(f"Ya existe un frame o malla llamado {name!r}.")
        if frame not in self._frames:
            raise KeyError(f"No existe el frame {frame!r}.")
        if not isinstance(mesh, self._trimesh.Trimesh):
            raise TypeError("mesh debe ser una instancia de trimesh.Trimesh.")

        opacity = float(opacity)
        if not 0.0 <= opacity <= 1.0:
            raise ValueError("opacity debe estar entre 0 y 1.")

        local_matrix = self._validar_matriz(
            np.eye(4) if transform is None else transform,
            "transform",
        )
        polydata = self._a_polydata(mesh, self._pv)

        # El nodo interno de la geometria es hijo del frame del robot.
        node_name = f"{self._MESH_NODE_PREFIX}{name}"
        self._scene.add_geometry(
            mesh,
            node_name=node_name,
            geom_name=name,
            parent_node_name=frame,
            transform=local_matrix,
        )

        matrix_world, _ = self._scene.graph.get(
            node_name, self._base_frame
        )

        try:
            actor = self._plotter.add_mesh(
                polydata,
                name=f"actor::{name}",
                color=color,
                opacity=opacity,
                smooth_shading=smooth_shading,
                user_matrix=matrix_world,
                reset_camera=not self._actors,
                render=False,
            )
        except Exception:
            # Evita dejar una geometria sin actor si PyVista rechaza el mesh.
            self._scene.delete_geometry(name)
            raise

        self._mesh_nodes[name] = node_name
        self._actors[name] = actor
        return actor

    # ------------------------------------------------------------------
    # API publica: transformaciones
    # ------------------------------------------------------------------

    def set_transform(self, name: str, matrix: Any) -> None:
        """Actualiza la transformacion LOCAL de un frame respecto a su padre."""
        self.update_transforms({name: matrix}, space="local")

    def update_transforms(
        self,
        transforms: Mapping[str, Any],
        space: str = "local",
    ) -> None:
        """Actualiza varios frames y sincroniza los actores una sola vez.

        Parameters
        ----------
        transforms:
            Diccionario ``{nombre_frame: matriz_4x4}``.
        space:
            ``"local"`` si las matrices son relativas al padre de cada frame;
            ``"world"`` si son relativas al frame raiz de la escena.

        Si se actualizan simultaneamente un padre y un hijo en espacio global,
        se usan las matrices globales nuevas de ambos para calcular las
        transformaciones locales correspondientes.
        """
        self._comprobar_abierta()

        if not isinstance(transforms, Mapping):
            raise TypeError("transforms debe ser un mapping nombre-matriz.")
        if space not in {"local", "world"}:
            raise ValueError("space debe ser 'local' o 'world'.")
        if not transforms:
            return

        matrices = {}
        for name, matrix in transforms.items():
            if name not in self._frames:
                raise KeyError(f"No existe el frame {name!r}.")
            if name == self._base_frame:
                raise ValueError("No se puede modificar la transformacion del frame raiz.")
            matrices[name] = self._validar_matriz(matrix, f"transforms[{name!r}]")

        if space == "local":
            matrices_local = matrices
        else:
            matrices_local: dict[str, np.ndarray] = {}
            for name, matrix_world in matrices.items():
                parent = self._frames[name]
                if parent is None:
                    raise RuntimeError(f"El frame {name!r} no tiene padre.")

                if parent in matrices:
                    parent_world = matrices[parent]
                else:
                    parent_world = self.get_world_transform(parent)

                try:
                    matrices_local[name] = np.linalg.solve(
                        parent_world, matrix_world
                    )
                except np.linalg.LinAlgError as exc:
                    raise ValueError(
                        f"La transformacion global del padre {parent!r} "
                        "no es invertible."
                    ) from exc

        # Todas las matrices se validan y calculan antes de modificar el grafo.
        for name, matrix_local in matrices_local.items():
            parent = self._frames[name]
            self._scene.graph.update(
                frame_to=name,
                frame_from=parent,
                matrix=matrix_local,
            )

        self._sincronizar_actores()

    def get_world_transform(self, name: str) -> np.ndarray:
        """Devuelve la matriz global de un frame o malla respecto a la raiz."""
        self._comprobar_abierta()
        node_name = self._nodo_de(name)

        if node_name == self._base_frame:
            return np.eye(4, dtype=float)

        matrix, _ = self._scene.graph.get(
            node_name, self._base_frame
        )
        return np.asarray(matrix, dtype=float).copy()

    # ------------------------------------------------------------------
    # API publica: ventana y renderizado
    # ------------------------------------------------------------------

    def render(self) -> None:
        """Solicita a PyVista renderizar la escena actual."""
        self._comprobar_abierta()
        self._plotter.render()

    def show(self, **kwargs: Any) -> Any:
        """Muestra la ventana interactiva de PyVista."""
        self._comprobar_abierta()
        return self._plotter.show(**kwargs)

    def close(self) -> None:
        """Cierra la ventana y libera los recursos de PyVista."""
        if not self._closed:
            self._plotter.close()
            self._closed = True

    # ------------------------------------------------------------------
    # Propiedades de consulta
    # ------------------------------------------------------------------

    @property
    def frames(self) -> tuple[str, ...]:
        """Nombres de los frames registrados, incluido el frame raiz."""
        return tuple(self._frames.keys())

    @property
    def meshes(self) -> tuple[str, ...]:
        """Nombres publicos de las mallas agregadas a la escena."""
        return tuple(self._mesh_nodes.keys())

    @property
    def trimesh_scene(self) -> Any:
        """Escena Trimesh subyacente, disponible para consultas avanzadas."""
        return self._scene

    @property
    def plotter(self) -> Any:
        """Plotter PyVista subyacente, disponible para personalizacion avanzada."""
        return self._plotter
