# Documentación de SimpleRobotics
**Versión documentada:** 1.0.5.1

**Toolbox MATLAB de referencia:** Dr. César A. Chávez Olivares 

**Traducción y desarrollo en Python:** Ing. Leonardo Andrey Gaspar Mejía

## 1. Propósito
SimpleRobotics es una biblioteca educativa diseñada para el estudio y análisis de transformaciones homogéneas, orientación, cinemática directa y la representación gráfica de mecanismos robóticos en un entorno 3D. A diferencia de otras herramientas que automatizan la generación de cadenas cinemáticas (como las basadas estrictamente en parámetros de Denavit-Hartenberg), SimpleRobotics permite al usuario construir modelos definiendo las transformaciones de manera explícita entre eslabones y sistemas de coordenadas.

Esta flexibilidad en la organización geométrica facilita la descripción de cadenas seriales complejas y la visualización de diagramas cinemáticos generales. Además, ofrece herramientas para representar los elementos del robot mediante primitivas geométricas (líneas, cilindros, prismas), sistemas de coordenadas o mallas STL.

El desarrollo de la versión en Python toma como base la toolbox Simple Robotics Toolbox 1.0.5v publicada el 11 de oct 2026 creada por el Dr. César A. Chávez-Olivares. El objetivo principal es preservar su enfoque didáctico y convenciones de uso. Se recomienda verificar los resultados de cada función de manera aislada antes de asumir una equivalencia numérica completa con la versión original de MATLAB en casos complejos.

**Liga de referencia de la Toolbox original:** https://la.mathworks.com/matlabcentral/fileexchange/80137-simple-robotics-toolbox

## 1.2. Contacto, consultas y reporte de errores

Si tienes dudas sobre la instalación, el uso de SimpleRobotics o el comportamiento de alguna función, puedes ponerte en contacto con el responsable de la adaptación a Python mediante los siguientes correos electrónicos:

- **Correo de contacto:** leogasmejob@gmail.com
- **Correo alternativo:** gasmejleoand@gmail.com

### Reporte de errores (*bugs*)

Si encuentras un error, un comportamiento inesperado o una discrepancia entre los resultados de SimpleRobotics y los de la toolbox original de MATLAB, se recomienda incluir la siguiente información en el mensaje:

- **Versión de SimpleRobotics** utilizada.
- **Versión de Python** y sistema operativo.
- **Función involucrada** y descripción breve del problema.
- **Código mínimo para reproducir el error**, cuando sea posible.
- **Resultado obtenido y resultado esperado**.
- **Mensaje de error completo** o captura de pantalla, si corresponde.

Esta información facilitará la identificación del problema y permitirá determinar si se trata de un error de implementación, una diferencia numérica o una cuestión relacionada con las convenciones de la toolbox original.

Los reportes y sugerencias serán útiles para documentar limitaciones, mejorar los ejemplos y orientar futuras revisiones de la biblioteca.

---

## 2. Instalación y requisitos

### 2.1 Instalación local

La instalación se realiza directamente desde el código fuente local. Abre una terminal en la carpeta raíz del proyecto, donde se encuentra `pyproject.toml`, y ejecuta:

```bash
python -m pip install -e .
```

El modo editable (`-e`) permite que los cambios en el código local se reflejen sin reinstalar el paquete. Para una instalación local no editable, utiliza:

```bash
python -m pip install .
```

Los comandos utilizan el intérprete asociado al ejecutable `python` de la terminal. Comprueba que VS Code o Jupyter utilicen ese mismo intérprete.

### 2.2 Instalación desde PyPI (pendiente de publicación)

Pendiente de publicación. Esta sección se completará cuando la
biblioteca esté disponible en PyPI y se confirme su nombre de
distribución.

### 2.3 El proyecto declara las siguientes dependencias:

- **NumPy:** operaciones matriciales y cálculos numéricos.
- **Matplotlib:** representación gráfica bidimensional y tridimensional.
- **SymPy:** operaciones y expresiones simbólicas.
- **trimesh:** lectura y manipulación de mallas STL.

## 3. Estructura del Proyecto

El código fuente está estructurado de la siguiente manera:

```text
SimpleRobotics/
pyproject.toml
setup.py
README.md
Documentacion.md
src/
SimpleRobotics/
__init__.py
transforms.py
plotting.py
formatting.py
```

---

## 4. Convenciones Matemáticas y de Uso

### 4.1 Unidades Angulares

Por defecto, las funciones trigonométricas y geométricas asumen que los ángulos se ingresan en **radianes**. Las funciones que aceptan grados incluyen explícitamente el sufijo `_grados` en su nombre (por ejemplo, `Rot_RPY_grados`).

### 4.2 Multiplicación Matricial y Transformaciones

Las funciones espaciales se dividen en dos grupos principales:

*   **Rotaciones puras (3x3):** `rotx3`, `roty3`, `rotz3`.

*   **Transformaciones homogéneas (4x4):** `rotx`, `roty`, `rotz` (rotaciones integradas en 4x4) y `trans` (traslación).

En Python (mediante NumPy), el operador recomendado para la multiplicación de matrices es `@`. **Atención:** El orden de la multiplicación es crítico (`A @ B ≠ B @ A`).

**Ejemplo de composición:**

```python
import numpy as np

from SimpleRobotics import rotz, trans

# Compone una rotación en Z y una traslación. En vectores columna, el factor derecho actúa primero.

H = rotz(np.pi / 4) @ trans(0.2, 0.0, 0.1)
```

### 4.3 Transformación de coordenadas

Para transformar un punto con una matriz homogénea **4x4**, represéntalo con cuatro componentes y coordenada homogénea igual a `1`. El siguiente ejemplo es independiente y usa un vector columna explícito:

```python
import numpy as np
from SimpleRobotics import rotz, trans

H = rotz(np.pi / 4) @ trans(0.2, 0.0, 0.1)
p = np.array([[0.5], [0.5], [0.0], [1.0]])
p_transformado = H @ p
posicion_xyz = p_transformado[:3, 0]
print(posicion_xyz)
```

En esta composición, el factor de la derecha actúa primero sobre los puntos representados como vectores columna.

---

## 5. Referencia de Funciones: Transformaciones y Orientación

Estas funciones residen en `transforms.py`. Salvo que se indique lo contrario, se pueden importar desde `SimpleRobotics`. La función `christoffel` se importa desde `SimpleRobotics.transforms`, porque no está exportada en el nivel principal del paquete.

| Función | Descripción y Uso |
| :--- | :--- |
| `deg2rad(grados)` | Convierte un valor de grados a radianes. |
| `rad2deg(radianes)` | Convierte un valor de radianes a grados. |
| `rotx3(theta)` / `roty3(theta)` / `rotz3(theta)` | Devuelve una matriz de rotación de **3x3** alrededor del eje X, Y o Z, respectivamente. |
| `rotx(theta)` / `roty(theta)` / `rotz(theta)` | Devuelve una matriz de transformación homogénea de **4x4** representando una rotación pura alrededor de X, Y o Z. |
| `trans(x, y, z)` | Devuelve una transformación homogénea **4x4** de traslación pura. |
| `Rot_RPY(phi, theta, psi)` | Construye una matriz **3x3** mediante la composición `Rz(phi) @ Ry(theta) @ Rx(psi)`. Los ángulos se expresan en radianes. |
| `Rot_RPY_grados(phi, theta, psi)` | Aplica la misma composición de `Rot_RPY`, pero recibe los tres ángulos en grados. |
| `Rot_eje(k, theta)` | Construye una rotación **3x3** alrededor del eje `k` y del ángulo `theta`. `k` debe tener tres componentes y ser un vector unitario; la función no normaliza el eje automáticamente. |
| `Eje_theta(H)` | Extrae el par (eje `Lambda`, ángulo `theta`) de una transformación homogénea **4x4**. Esta función no acepta una matriz de rotación aislada de **3x3**. |
| `Eje_theta_grados(H)` | Igual que `Eje_theta`, pero devuelve el ángulo en grados; `H` debe ser **4x4**. |
| `RPY(H)` | Extrae una terna angular de una matriz **3x3** o **4x4**. La implementación devuelve los ángulos en el orden correspondiente a `Rz(phi) @ Ry(theta) @ Rx(psi)`: `(phi, theta, psi)`. |
| `RPY_grados(H)` | Devuelve la misma terna de `RPY`, pero en grados y en el mismo orden `(phi, theta, psi)`. |
| `DH(theta, d, a, alpha)` | Genera la matriz de transformación 4x4 correspondiente a los parámetros de Denavit-Hartenberg estándar para un eslabón. |
| `H_inv(H)` | Calcula la inversa de una transformación homogénea rígida **4x4**. La parte de rotación debe ser ortonormal. |
| `Rot_Q(e1, e2, e3, e4)` | Devuelve una matriz de rotación **3x3** a partir de los componentes del cuaternión en el orden `[e1, e2, e3, e4]`. La función no normaliza el cuaternión; usa componentes compatibles con la convención implementada por esta biblioteca. |
| `Quaternions(H)` | Calcula los cuatro componentes del cuaternión a partir de la submatriz de rotación de `H` (admite **3x3** o **4x4**). La fórmula actual puede ser problemática cerca de rotaciones de 180 grados. |
| `Axis2Quaternions(Lambda, theta)` | Convierte una representación eje-ángulo en cuatro componentes de cuaternión. `Lambda` debe ser un eje unitario de tres componentes; conserva la convención de signo propia de la implementación (`e1 = -cos(theta/2)`). |
| `ejes(MatA, t)` | Devuelve cuatro puntos homogéneos: origen y extremos de los ejes X, Y y Z de una transformación **4x4**. No los dibuja por sí sola. |
| `christoffel(M, q, i, j, k)` | Calcula un símbolo de Christoffel con matrices/vectores de SymPy. Los índices `i`, `j` y `k` siguen numeración desde **1**, como en MATLAB. Importar con `from SimpleRobotics.transforms import christoffel`. |

> **Convención y singularidades:** `Rot_RPY(phi, theta, psi)` construye `Rz(phi) @ Ry(theta) @ Rx(psi)` y `RPY(H)` devuelve la terna en ese mismo orden `(phi, theta, psi)`. No debe suponerse que esa terna coincide con el orden usado por otra biblioteca bajo las etiquetas `roll, pitch, yaw`; comprueba la convención antes de intercambiar datos. La extracción también tiene singularidades cuando el ángulo intermedio se aproxima a ±π/2, y `Quaternions(H)` merece pruebas adicionales cerca de rotaciones de 180 grados.

### Profundización en SymPy para Transformaciones Simbólicas

SimpleRobotics admite, en una gran porción de sus funciones, la introducción de variables simbólicas de `SymPy`. Esto resulta especialmente útil en la obtención de matrices de transformación paramétricas y en el análisis analítico de la cinemática de manipuladores.

**Ejemplo de uso de SymPy:**

```python
import sympy as sp

from SimpleRobotics import rotz, rotx, trans, matriz_a_texto

# 1. Declarar variables simbólicas

theta1, d1, a1, alpha1 = sp.symbols('theta1 d1 a1 alpha1')

# 2. Generar transformación genérica (e.g., convención de Denavit-Hartenberg estándar)

A1 = rotz(theta1) @ trans(a1, 0, d1) @ rotx(alpha1)

# 3. Presentar en pantalla la matriz resultante de forma comprensible

print("Matriz de Transformación Simbólica A1:")

print(matriz_a_texto(A1))
```

Al utilizar símbolos, las funciones como `Eje_theta` o `RPY` aplicarán internamente simplificaciones algebraicas cuando sea pertinente, evitando la evaluación numérica y manteniendo la pureza de las expresiones simbólicas. Es crucial tener en cuenta que las operaciones simbólicas presentan un costo computacional mayor al de las numéricas.

---

## 6. Generación de trayectorias y análisis numérico

SimpleRobotics incluye funciones para aproximar derivadas y generar perfiles de posición y velocidad. Para los métodos de derivación, `q` y `t` deben contener la misma cantidad de muestras; se recomienda que el tiempo sea estrictamente creciente.

| Función | Descripción |
| :--- | :--- |
| `derivada_numerica(q, t)` | Diferencias hacia atrás en puntos interiores; el primer resultado queda en cero y el último copia el anterior. |
| `derivada_numerica2(q, t)` | Diferencias hacia atrás; ambos extremos copian el valor del punto interior vecino. |
| `derivada_numerica_central(q, t)` | Diferencias centrales en puntos interiores; los extremos copian el valor vecino. |
| `interpolacion_lineal(q_i, q_f, t_i, t_f, t)` | Evalúa la interpolación lineal en el tiempo `t`. |
| `interpolacion_lineal_vector(q_i, q_f, t)` | Devuelve perfiles de posición y velocidad para el vector de tiempos `t`. |
| `interpolacion_cubica(q_i, q_f, qp_i, qp_f, t_i, t_f, t)` | Intenta evaluar una interpolación cúbica con condiciones de posición y velocidad en los extremos. La implementación actual no satisface esas condiciones para todos los intervalos; revisa la advertencia de validación antes de usarla. |
| `interpolacion_cubica_vector(q_i, q_f, qp_i, qp_f, t)` | Devuelve perfiles de posición y velocidad para el vector de tiempos; comparte el problema de condiciones de frontera descrito abajo. Requiere al menos tres muestras para calcular la velocidad. |
| `interpolacion_tramos(q_i, q_f, Vmax, Amax, t)` | Evalúa un perfil por tramos a partir de límites de velocidad y aceleración. |
| `interpolacion_tramos_vector(q_i, q_f, Vmax, Amax, t)` | Devuelve perfiles de posición y velocidad por tramos. |
| `Energia_robot(qp, tau, t)` | Integra numéricamente la potencia aproximada `sum(qp * tau)`; `qp` y `tau` deben ser matrices de igual tamaño. |
| `normaL2(e, t)` | Calcula una norma L2 temporal normalizada para una matriz de señales `e` de forma `(n_muestras, n_señales)`. No admite una entrada unidimensional. |

### Ejemplo: derivada numérica de una trayectoria

```python
import numpy as np
from SimpleRobotics import derivada_numerica_central

tiempos = np.linspace(0.0, 2.0, num=100)
posiciones_x = np.sin(tiempos)
velocidades_x = derivada_numerica_central(posiciones_x, tiempos)
print(velocidades_x[:5])
```

`derivada_numerica_central` calcula diferencias centrales en las muestras interiores. En la implementación actual, los extremos copian el valor derivado de la muestra adyacente; no se calcula allí una diferencia unilateral independiente. La interpolación cúbica también requiere corrección y pruebas adicionales: durante la revisión, un caso con duración `t_f - t_i = 2` y velocidades de extremo distintas de cero no alcanzó la posición final solicitada. Consulta `INFORME_VERIFICACION_EJEMPLOS.md` para el detalle.

## 7. Formato y Visualización de Matrices en Texto

El módulo `formatting.py` incluye herramientas útiles para la depuración y la presentación de datos, especialmente útiles cuando se trabaja con matrices simbólicas de SymPy o arreglos numéricos con muchos decimales.

*   `matriz_a_texto(matriz, precision=4)`: Devuelve una cadena de texto formateada y alineada de la matriz.

*   `mostrar_matriz(matriz, precision=4)`: Imprime directamente en consola el resultado de `matriz_a_texto`.

**Ejemplo de uso:**

```python
from SimpleRobotics import trans, mostrar_matriz

T = trans(1.23456, 9.87654, 0.0)

mostrar_matriz(T, precision=2)
```

---

## 8. Representación Gráfica y Geometría 3D

El módulo `plotting.py` contiene todas las funciones para visualizar al robot. Para utilizarlas adecuadamente, es necesario instanciar primero una figura de Matplotlib con soporte 3D y pasar el objeto `Axes3D` a las funciones mediante el argumento `ax`.

### 8.1 Preparación del entorno 3D

```python
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
```

Pasa `ax=ax` a las funciones de dibujo para que los elementos se añadan a esos mismos ejes.

### 8.2 Primitivas de Dibujo

En la mayoría de estas funciones, el parámetro `K` u `H` representa una matriz de transformación homogénea (4x4) que dicta dónde y cómo se orientará el elemento gráfico en el espacio.

**Elementos Estructurales:**

| Función | Descripción |
| :--- | :--- |
| `eslabon(po, pf, c="k", lw=2, ax=None)` | Dibuja un segmento de línea (representando un eslabón simple) entre los vectores de posición 3D `po` y `pf`. |
| `cilindro(K, alto, radio, dif, ax=None)` | Renderiza un cilindro. `K` determina la base, y `dif` permite desfasarlo longitudinalmente. |
| `tubo(K, alto, radio, color, ax=None)` | Renderiza la superficie externa de un cilindro. |
| `tubo2(K, alto, radio, color, nalpha, ...)` | Versión del tubo que permite controlar la transparencia (canal alfa con `nalpha` ∈ [0,1]). |
| `cono(K, alto, radio, color, ax=None)` | Dibuja un cono. La matriz `K` ubica el centro de la base del cono. |
| `flecha(K, alto, color, ax=None)` | Representa gráficamente un vector (eje) mediante un cilindro coronado por un cono. |
| `esfera(K, radio, color, ax=None)` | Coloca una esfera de tamaño `radio` en el origen del sistema descrito por `K`. |
| `gripper(H, L, lw, ax=None)` | Dibuja una abstracción geométrica de un efector final (pinza). |
| `prisma_rectangular(K, ancho_x, largo_y, alto_z, ...)`| Dibuja un paralelepípedo sólido. `prisma_rectangularC` y `prisma_rectangularC2` ofrecen variantes de color y transparencia. |
| `piramide(K, alto, lado, color, ax=None)` | Crea una pirámide de base cuadrada. |
| `DibujaPlano(LX, LY, K, nalpha, ax=None)` | Crea una superficie plana rectangular en la orientación definida. |
| `linea_punteada(po, pf, ax=None)` | Similar a `eslabon`, pero con estilo de trazo discontinuo. |

**Integración de Archivos STL (Mallas complejas):**

| Función | Descripción |
| :--- | :--- |
| `Load_STL(archivo)` | Lee un archivo STL con `trimesh` y devuelve un objeto con `vertices`, `faces`, `normals`, `colors` y `STLtitle`. Si el archivo no existe, lanza `ValueError`. |
| `eslabon_STL(H, solido, RGBcolor, ax=None)` | Posiciona, orienta y dibuja la malla `solido` (obtenida con `Load_STL`) en el entorno 3D aplicando la transformación `H`. |

**Representación de Sistemas y Cinemática:**

| Función | Descripción |
| :--- | :--- |
| `Sistema(M, t, lx, ly, lz, tf, ax=None)` | Dibuja los tres ejes como líneas. `t` es la longitud de los ejes; `lx`, `ly`, `lz` son sus etiquetas y `tf` el tamaño de fuente. |
| `Sistema3D(M, t, lx, ly, lz, tf, ax=None)` | Dibuja los ejes mediante flechas y etiquetas. `Sistema3Dbool` permite mostrar u ocultar cada eje mediante `aparecer`. |
| `ejes3D(Po, Px, Py, Pz, cx, cy, cz, lw, ...)` | Dibuja ejes explícitos definiendo el origen (`Po`) y los puntos finales de cada vector coordenado. |
| `giro_z(K, theta_max, r, lth, lpos, tf, ...)` | Dibuja el arco indicativo de una rotación cinemática en el plano XY local. `giroZ` es una función análoga. |
| `desplazamiento_z(K, altura, offsetXY, ...)` | Dibuja una flecha indicativa de un movimiento de traslación cinemático. |
| `distancia_z(K, altura, offsetXY, ld, ...)` | Dibuja cotas geométricas (líneas de acotación) para indicar dimensiones en los diagramas. |

### 8.3 Ejemplo completo de visualización

El ejemplo arma una cadena cinemática sencilla de dos eslabones. En `Sistema`, el segundo argumento es la longitud de los ejes, no el nombre de la articulación; las etiquetas se pasan en los argumentos `lx`, `ly` y `lz`.

```python
import numpy as np
import matplotlib.pyplot as plt
from SimpleRobotics import trans, rotz, roty, eslabon, Sistema

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")

L1, L2 = 0.5, 0.4
H0 = trans(0, 0, 0)
q1 = np.deg2rad(45)
H1 = rotz(q1) @ trans(L1, 0, 0)
q2 = np.deg2rad(-30)
H2 = H1 @ roty(q2) @ trans(L2, 0, 0)

eslabon(H0[:3, 3], H1[:3, 3], c="blue", lw=4, ax=ax)
eslabon(H1[:3, 3], H2[:3, 3], c="red", lw=4, ax=ax)

Sistema(H0, 0.2, "x_0", "y_0", "z_0", 10, ax=ax)
Sistema(H1, 0.15, "x_1", "y_1", "z_1", 8, ax=ax)
Sistema(H2, 0.1, "x_2", "y_2", "z_2", 8, ax=ax)
ax.text(*(H0[:3, 3] + np.array([0.02, 0.02, 0.02])), "Base")
ax.text(*(H1[:3, 3] + np.array([0.02, 0.02, 0.02])), "J1")
ax.text(*(H2[:3, 3] + np.array([0.02, 0.02, 0.02])), "TCP")

ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_zlabel("Z (m)")
ax.set_box_aspect((1, 1, 1))
plt.title("Ejemplo cinemático SimpleRobotics")
plt.show()
```

## 9. Ejemplo especializado: orientación RPY

La implementación de esta versión compone `Rz(phi) @ Ry(theta) @ Rx(psi)`. La función `RPY(H)` devuelve los ángulos en el mismo orden posicional `(phi, theta, psi)`. No asumas que este orden coincide con la nomenclatura utilizada por otras bibliotecas para `roll`, `pitch` y `yaw`; comprueba la convención antes de intercambiar datos.

```python
import numpy as np
from SimpleRobotics import Rot_RPY, RPY

phi, theta, psi = 0.3, 0.4, -0.2
rotacion_3x3 = Rot_RPY(phi, theta, psi)

H = np.eye(4)
H[:3, :3] = rotacion_3x3

phi_obtenido, theta_obtenido, psi_obtenido = RPY(H)
print(f"phi: {phi_obtenido:.4f}, theta: {theta_obtenido:.4f}, psi: {psi_obtenido:.4f}")
```

La extracción presenta una singularidad cuando el ángulo intermedio `theta` se aproxima a `±pi/2`. Asimismo, la fórmula actual de `Quaternions(H)` requiere pruebas específicas cerca de rotaciones de 180 grados.

## 10. Consideraciones de uso y fiabilidad

La presente documentación ilustra las capacidades de SimpleRobotics en su versión actual. **El software se provee como una herramienta con fines educativos e investigativos.**

Recomendaciones críticas antes de su uso en plataformas físicas (robots reales) o simulaciones industriales complejas:

1.  **Tipado Dinámico:** Python no restringe los tipos de entrada. Cerciórese de no enviar un vector donde se espera una matriz o viceversa.

2.  **Unidades:** Verifique constantemente el uso de grados versus radianes, y la coherencia de unidades de longitud (metros o milímetros) entre funciones.

3.  **Límites Trigonométricos:** Implemente casos de prueba (Unit Tests) cerca de las fronteras de singularidad.

4.  **Desviación de MATLAB:** Aunque esta librería es una adaptación, el comportamiento de coma flotante y manejo numérico de SymPy/NumPy puede diferir marginalmente respecto a las funciones análogas en el núcleo de MATLAB.

5.  **Ejemplos de Referencia:** Para observar una gama mucho más extensa de modelos cinemáticos, animaciones avanzadas y aplicaciones de la librería en manipuladores industriales concretos, se remite al usuario a los **scripts de ejemplo incluidos en la Toolbox original de MATLAB del Dr. Chávez Olivares**. Dichos ejemplos sirven como guía arquitectónica para estructurar simulaciones complejas en la variante Python.

---

## 11. Créditos y autoría

*   **Autor de la Toolbox original en MATLAB:** Dr. César A. Chávez-Olivares.

*   **Desarrollo, adaptación, y traducción a Python:** Ing. Leonardo Andrey Gaspar Mejía.

Este proyecto reconoce la toolbox MATLAB original como referencia y presenta su adaptación en Python con fines educativos. Antes de redistribuir el código o la documentación derivados, conserva los avisos de autoría y revisa la licencia y los términos de uso aplicables a la obra original.
