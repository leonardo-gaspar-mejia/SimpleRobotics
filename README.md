# SimpleRobotics
**Biblioteca educativa de robótica en Python**  
**Versión:** 1.0.5.2

## Español

SimpleRobotics es una biblioteca educativa para estudiar y comprender la cinemática de manipuladores robóticos mediante transformaciones homogéneas. La construcción del modelo cinemático queda a criterio del usuario: las transformaciones entre eslabones y sistemas de coordenadas se definen explícitamente, en lugar de generarse automáticamente a partir de una tabla Denavit–Hartenberg.

Este enfoque permite representar distintas arquitecturas y diagramas cinemáticos, incluidos mecanismos paralelos y configuraciones como los paralelogramos presentes en algunos robots industriales. Los elementos del modelo pueden representarse mediante sistemas de coordenadas, líneas y primitivas geométricas, o mediante modelos sólidos en formato STL.

La biblioteca también incorpora herramientas de visualización y animación tridimensional para representar el movimiento de los manipuladores y actualizar sus configuraciones durante la ejecución. Para ello, utiliza herramientas como Matplotlib y PyVista, según el tipo de representación requerido.

La versión Python toma como referencia la toolbox MATLAB del **Dr. César A. Chávez-Olivares** y busca conservar su enfoque educativo y sus convenciones matemáticas, corrigiendo los problemas propios de la traducción cuando corresponde.

### Autoría y reconocimiento

- **Toolbox MATLAB original:** Dr. César A. Chávez-Olivares.
- **Traducción y desarrollo de la versión Python:** Ing. Leonardo Andrey Gaspar Mejía.

La inclusión de ambos créditos reconoce la autoría de la toolbox de referencia y el trabajo de traducción e implementación en Python. Antes de distribuir públicamente el proyecto, conserva los avisos de autoría y revisa las condiciones de uso de la toolbox original.

### Módulos

- `transforms.py`: rotaciones, traslaciones, transformaciones homogéneas, orientación, cuaterniones, derivadas e interpolación de trayectorias.
- `plotting.py`: representación tridimensional de eslabones, sistemas de coordenadas, primitivas geométricas, trayectorias y mallas STL.
- `formatting.py`: presentación legible de matrices numéricas y simbólicas.
- `animation.py`: construcción, actualización y animación de escenas tridimensionales para representar el movimiento de manipuladores robóticos.
- `RobotRR.py`: herramientas específicas para la construcción y visualización del manipulador RR.

### Instalación

Desde la carpeta raíz del proyecto, donde se encuentra `pyproject.toml`:

```bash
python -m pip install .
```

Para trabajar en modo editable durante el desarrollo:

```bash
python -m pip install -e .
```

El proyecto utiliza NumPy, Matplotlib, SymPy, trimesh y PyVista. Se recomienda instalarlo en un entorno virtual.

### Ejemplo básico

```python
import numpy as np
import matplotlib.pyplot as plt
from SimpleRobotics import trans, rotz, eslabon

# Transformación homogénea: rotación alrededor de Z y traslación.
H = rotz(np.deg2rad(30)) @ trans(0.4, 0.0, 0.0)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

eslabon([0, 0, 0], H[:3, 3], ax=ax)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()
```

En NumPy, usa `@` para multiplicar matrices. Las funciones con sufijo `_grados` reciben o devuelven ángulos en grados; las demás funciones de orientación trabajan normalmente en radianes.

### Documentación

Consulta [`Documentacion.md`](Documentacion.md) para ver los módulos, las funciones principales, las convenciones y ejemplos de uso, incluyendo las herramientas de visualización y animación.

### Alcance

La biblioteca tiene fines educativos. Antes de emplear una función en una aplicación real, comprueba las dimensiones de entrada, las unidades, las singularidades y los casos límite relevantes. La equivalencia con MATLAB debe evaluarse función por función; la traducción no implica por sí sola una validación exhaustiva.

---

## English

SimpleRobotics is an educational Python library for studying and understanding the kinematics of robot manipulators using homogeneous transformations. The construction of the kinematic model is left to the user: transformations between links and coordinate frames are explicitly defined instead of being automatically generated from a Denavit–Hartenberg table.

This approach supports different kinematic architectures and diagrams, including parallel mechanisms and configurations such as the parallelograms found in some industrial robots. Model elements can be represented using coordinate frames, lines and geometric primitives, or solid models in STL format.

The library also incorporates three-dimensional visualization and animation tools to represent manipulator motion and update their configurations during execution. For this purpose, it uses tools such as Matplotlib and PyVista, depending on the required type of representation.

The Python version is based on the MATLAB toolbox by **Dr. César A. Chávez-Olivares**. It aims to preserve the original educational approach and mathematical conventions while addressing issues introduced by the Python translation when appropriate.

### Authorship and acknowledgment

- **Original MATLAB toolbox:** Dr. César A. Chávez-Olivares.
- **Python translation and development:** Eng. Leonardo Andrey Gaspar Mejía.

These credits distinguish the authorship of the reference toolbox from the work involved in translating and implementing it in Python. Before publicly redistributing the project, retain the original attribution notices and review the terms governing use of the MATLAB toolbox.

### Modules

- `transforms.py`: rotations, translations, homogeneous transformations, orientation representations, quaternions, numerical derivatives and trajectory interpolation.
- `plotting.py`: 3D visualization of links, coordinate frames, geometric primitives, trajectories and STL meshes.
- `formatting.py`: readable display of numeric and symbolic matrices.
- `animation.py`: construction, updating and animation of three-dimensional scenes to represent robotic manipulator motion.
- `RobotRR.py`: specific tools for constructing and visualizing the RR manipulator.

### Installation

From the project root, where `pyproject.toml` is located, run:

```bash
python -m pip install .
```

For editable installation during development:

```bash
python -m pip install -e .
```

The project uses NumPy, Matplotlib, SymPy, trimesh and PyVista. A virtual environment is recommended.

### Basic example

```python
import numpy as np
import matplotlib.pyplot as plt
from SimpleRobotics import trans, rotz, eslabon

# Homogeneous transformation: rotation around Z and translation.
H = rotz(np.deg2rad(30)) @ trans(0.4, 0.0, 0.0)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

eslabon([0, 0, 0], H[:3, 3], ax=ax)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()
```

Use `@` for NumPy matrix multiplication. Functions with the `_grados` suffix use degrees; other orientation functions normally use radians.

### Documentation

See [`Documentacion.md`](Documentacion.md) for the module overview, main functions, conventions and usage examples, including the visualization and animation tools.

### Scope

This library is intended for educational use. Before using a function in an application, check its input dimensions, units, singularities and relevant edge cases. MATLAB equivalence should be assessed function by function; a translation alone does not imply exhaustive validation.