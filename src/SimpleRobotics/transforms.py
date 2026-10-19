"""Rotaciones y traslaciones para robótica.

La API pública es única para valores numéricos y simbólicos:
- Si los argumentos son numéricos, las funciones devuelven ``numpy.ndarray``.
- Si algún argumento es una expresión de SymPy, devuelven matrices de SymPy.
- SymPy es opcional: solo se necesita para entradas simbólicas.

Convenciones:
- Los ángulos se expresan en radianes salvo en funciones con sufijo ``_grados``.
- Se utilizan vectores columna y matrices homogéneas 4x4.
- Las matrices siguen la convención de mano derecha.
- ``rotx3``, ``roty3`` y ``rotz3`` devuelven rotaciones 3x3.
- ``rotx``, ``roty`` y ``rotz`` devuelven rotaciones homogéneas 4x4.
- ``trans(x, y, z)`` devuelve una traslación homogénea 4x4.
- ``RPY(phi, theta, psi)`` sigue Rz(phi) @ Ry(theta) @ Rx(psi).
"""

from __future__ import annotations

import math
from math import pi
from math import sqrt
from typing import Any
import numpy as np
import sympy as sp

Array = np.ndarray

def deg2rad(valor_en_grados: float) -> float:
    """Convierte grados a radianes, conservando expresiones simbólicas."""
    if _usa_sympy(valor_en_grados):
        sp = _sympy()
        return valor_en_grados * sp.pi / 180
    return math.radians(valor_en_grados)

def rad2deg(valor_en_radianes: float) -> float:
    """Convierte radianes a grados, conservando expresiones simbólicas."""
    if _usa_sympy(valor_en_radianes):
        sp = _sympy()
        return valor_en_radianes * 180 / sp.pi
    return math.degrees(valor_en_radianes)

def _usa_sympy(*valores: Any) -> bool:
    """Detecta expresiones SymPy, también dentro de listas y arreglos de objetos."""

    def contiene_simbolos(valor: Any) -> bool:
        if type(valor).__module__.split(".", 1)[0] == "sympy":
            return True

        if isinstance(valor, np.ndarray) and valor.dtype == object:
            return any(contiene_simbolos(elemento) for elemento in valor.flat)

        if isinstance(valor, (list, tuple)):
            return any(contiene_simbolos(elemento) for elemento in valor)

        return False

    return any(contiene_simbolos(valor) for valor in valores)

def _sympy():
    """Importa SymPy solo cuando una operación simbólica lo necesita."""
    try:
        import sympy
    except ImportError as exc:
        raise ImportError(
            "Esta operación recibió valores simbólicos. Instala el extra con "
            "'python -m pip install -e \".[symbolic]\"' para utilizar SymPy."
        ) from exc
    return sympy

def _trig(theta: Any) -> tuple[Any, Any]:
    """Calcula coseno y seno con el backend apropiado para el argumento."""
    if _usa_sympy(theta):
        sp = _sympy()
        return sp.cos(theta), sp.sin(theta)
    return math.cos(theta), math.sin(theta)

def rotx3(theta: float) -> Array:
    """Devuelve una rotación 3x3 alrededor de X (radianes).

    Acepta números o expresiones SymPy. El tipo de salida depende de la entrada.
    """
    c, s = _trig(theta)
    filas = [
        [1, 0, 0],
        [0, c, -s],
        [0, s, c],
    ]
    return _sympy().Matrix(filas) if _usa_sympy(theta) else np.array(filas, dtype=float)

def roty3(theta: float) -> Array:
    """Devuelve una rotación 3x3 alrededor de Y (radianes)."""
    c, s = _trig(theta)
    filas = [
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c],
    ]
    return _sympy().Matrix(filas) if _usa_sympy(theta) else np.array(filas, dtype=float)

def rotz3(theta: float) -> Array:
    """Devuelve una rotación 3x3 alrededor de Z (radianes)."""
    c, s = _trig(theta)
    filas = [
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1],
    ]
    return _sympy().Matrix(filas) if _usa_sympy(theta) else np.array(filas, dtype=float)

def _homogeneous_rotation(rotation: Any) -> Any:
    """Inserta una matriz de rotación 3x3 en una matriz homogénea 4x4.

    Se revisan todos los elementos para detectar matrices simbólicas. En Rx,
    por ejemplo, el elemento [0, 0] siempre es 1, incluso cuando el ángulo
    es simbólico; revisar solo ese elemento seleccionaría incorrectamente NumPy.
    """
    es_simbolica = any(
        _usa_sympy(rotation[i, j])
        for i in range(rotation.shape[0])
        for j in range(rotation.shape[1])
    )

    if es_simbolica:
        sp = _sympy()
        result = sp.eye(4)
        result[:3, :3] = rotation
        return result

    result = np.eye(4, dtype=float)
    result[:3, :3] = rotation
    return result

def rotx(theta: float) -> Array:
    """Devuelve una rotación homogénea 4x4 alrededor de X (radianes).

    Con un ángulo numérico devuelve ``numpy.ndarray``; con uno simbólico,
    devuelve una matriz SymPy. No se necesita una función ``rotx_sym`` aparte.
    """
    return _homogeneous_rotation(rotx3(theta))

def roty(theta: float) -> Array:
    """Devuelve una rotación homogénea 4x4 alrededor de Y (radianes)."""
    return _homogeneous_rotation(roty3(theta))

def rotz(theta: float) -> Array:
    """Devuelve una rotación homogénea 4x4 alrededor de Z (radianes).

    Acepta valores numéricos y expresiones SymPy mediante la misma función.
    """
    return _homogeneous_rotation(rotz3(theta))

def _normaliza_entero_float(valor: Any) -> Any:
    """Convierte floats que representan enteros exactos en enteros Python.

    Por ejemplo, 2.0 pasa a 2. Esto evita que una traslación escrita con
    literales como ``trans(1.0, 2.0, 3.0)`` introduzca ``Float`` en una
    expresión de SymPy al multiplicarse después por una rotación simbólica.
    Los valores fraccionarios y no finitos se conservan sin cambios.
    """
    if isinstance(valor, (float, np.floating)):
        numero = float(valor)
        if math.isfinite(numero) and numero.is_integer():
            return int(numero)
    return valor

def trans(x: float, y: float, z: float) -> Array:
    """Devuelve una traslación homogénea 4x4 para (x, y, z).

    Si alguna coordenada es simbólica, devuelve una matriz SymPy. Los
    floats que representan enteros exactos se normalizan para evitar
    decimales innecesarios en composiciones simbólicas.
    """
    x, y, z = (_normaliza_entero_float(v) for v in (x, y, z))
    filas = [
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ]
    if _usa_sympy(x, y, z):
        return _sympy().Matrix(filas)

    # Los enteros se conservan como enteros; una coordenada fraccionaria
    # hace que NumPy seleccione el tipo numérico que corresponde.
    dtype = np.asarray([x, y, z]).dtype
    result = np.eye(4, dtype=dtype)
    result[:3, 3] = [x, y, z]
    return result

def Rot_RPY(phi: float, theta: float, psi: float) -> Array:
    """Compone la rotación RPY: Rz(phi) @ Ry(theta) @ Rx(psi).

    Los ángulos se expresan en radianes. Si alguno es simbólico, la operación
    completa se realiza con matrices SymPy; de lo contrario usa NumPy.
    """
    if _usa_sympy(phi, theta, psi):
        sp = _sympy()
        phi, theta, psi = (sp.sympify(v) for v in (phi, theta, psi))
    return rotz3(phi) @ roty3(theta) @ rotx3(psi)

def Rot_RPY_grados(phi: float, theta: float, psi: float) -> Array:
    """Compone una rotación RPY; recibe los tres ángulos en grados."""
    if _usa_sympy(phi, theta, psi):
        sp = _sympy()
        factor = sp.pi / 180
        return Rot_RPY(phi * factor, theta * factor, psi * factor)
    return Rot_RPY(math.radians(phi), math.radians(theta), math.radians(psi))

def Rot_eje(k: Any, theta: Any) -> Array:

    if len(k) != 3:
        raise ValueError("El eje k debe tener exactamente 3 componentes.")

    kx, ky, kz = k

    es_simbolica = _usa_sympy(kx, ky, kz, theta)

    if es_simbolica:

        sp = _sympy()
        kx, ky, kz, theta = (
            sp.sympify(v) for v in (kx, ky, kz, theta)
        )

    c, s = _trig(theta)
    Vt = 1 - c

    filas = [
        [kx*kx*Vt+c, kx*ky*Vt-kz*s, kx*kz*Vt+ky*s],
        [kx*ky*Vt+kz*s, ky*ky*Vt+c, ky*kz*Vt-kx*s],
        [kx*kz*Vt-ky*s, ky*kz*Vt+kx*s, kz*kz*Vt+c]
]
    return _sympy().Matrix(filas) if es_simbolica else np.array(filas, dtype=float)

def Eje_theta(H: Any) -> tuple[Any, Any]:

    es_simbolica = _usa_sympy(H)

    if es_simbolica:

        sp = _sympy()
        H_sym = sp.Matrix(H)

        if H_sym.shape != (4, 4):
            raise ValueError("H debe ser una matriz de transformación 4x4.")

        R_sym = H_sym[:3, :3]

        if R_sym.free_symbols:

            trace = sum(R_sym[i, i] for i in range(3))
            theta = sp.acos((trace - 1) / 2)

            Lambda = sp.Matrix([
                (R_sym[2, 1] - R_sym[1, 2]) / (2 * sp.sin(theta)),
                (R_sym[0, 2] - R_sym[2, 0]) / (2 * sp.sin(theta)),
                (R_sym[1, 0] - R_sym[0, 1]) / (2 * sp.sin(theta))
            ])

            norma = sp.sqrt(sum(componente**2 for componente in Lambda))
            Lambda = Lambda / norma

            return Lambda, theta

        else:

            H = np.eye(4, dtype=float)
            H[:3, :3] = np.asarray(R_sym.tolist(), dtype=float)

    else:

        H = np.asarray(H, dtype=float)

    if  H.shape != (4, 4):

        raise ValueError("H debe ser una matriz de trasformacion homogenea")

    R = H[:3, :3]

    val_cos = (np.trace(R) - 1) / 2
    val_cos = max(-1.0, min(1.0, float(val_cos)))
    theta = math.acos(val_cos)

    tol = 1e-6

    if theta < tol:

        theta = 0.0
        Lambda = np.array([1.0, 0.0, 0.0])

    elif abs(theta - pi) < tol:

        theta = pi

        abs_lx = sqrt(max(0.0, (R[0, 0] + 1) / 2))
        abs_ly = sqrt(max(0.0, (R[1, 1] + 1) / 2))
        abs_lz = sqrt(max(0.0, (R[2, 2] + 1) / 2))

        if abs_lx >= abs_ly and  abs_lx >= abs_lz:

            lx = abs_lx
            ly = R[0, 1] / (2 * lx)
            lz = R[0, 2] / (2 * lx)

        elif abs_ly >= abs_lx and abs_ly >= abs_lz:

            ly = abs_ly
            lx = R[0, 1] / (2 * ly)
            lz = R[0, 2] / (2 * ly)

        else:
            lz = abs_lz
            lx = R[0, 1] / (2 * lz)
            ly = R[0, 2] / (2 * lz)

        Lambda = np.array([lx, ly, lz], dtype=float)

    else:

        lx = (R[2, 1] - R[1, 2]) / (2 * math.sin(theta))
        ly = (R[0, 2] - R[2, 0]) / (2 * math.sin(theta))
        lz = (R[1, 0] - R[0, 1]) / (2 * math.sin(theta))

        Lambda = np.array([lx, ly, lz], dtype=float)

    norma = np.linalg.norm(Lambda)

    if norma == 0 or not math.isfinite(norma):
        raise ValueError("No se pudo calcular un eje de rotación válido. "
        "Comprueba que H represente una transformación rígida.")

    Lambda = Lambda / norma

    return Lambda, theta

def Eje_theta_grados(H: Any) -> tuple[Any, Any]:

    Lambda, theta =Eje_theta(H)
        
    return Lambda, rad2deg(theta)

def RPY(H: Any) -> tuple[Any, Any, Any]:

    es_simbolica = _usa_sympy(H)
    R = H[:3, :3]

    if es_simbolica:
        sp = _sympy()
        Yaw = sp.atan2(R[2,1],R[2,2])
        Roll = sp.atan2(R[1,0], R[0,0])
        Pitch = sp.atan2(-R[2,0],sp.sqrt(R[0,0]**2 + (R[1,0])**2))
    else:

        r31 = R[2, 0]
        tol = 1e-6

        if abs(r31 + 1) < tol:

            Pitch = pi / 2
            Yaw = 0
            Roll = math.atan2(R[1, 2], R[1, 1])

        elif abs(r31 - 1) < tol:

            Pitch = -pi / 2
            Yaw = 0
            Roll = math.atan2(-R[1, 2], R[1, 1])

        else:
            Yaw = math.atan2(R[2,1],R[2,2])
            Roll = math.atan2(R[1,0], R[0,0])
            Pitch = math.atan2(-R[2,0],sqrt(R[0,0]**2 + (R[1,0])**2))

    return Roll, Pitch, Yaw

def RPY_grados(H: Any) -> tuple[Any, Any, Any]:

    Roll, Pitch, Yaw=RPY(H)

    return rad2deg(Roll), rad2deg(Pitch), rad2deg(Yaw)

def DH(theta: Any, d: Any, a: Any, alpha: Any) -> Array:

    M = rotz(theta)@trans(a,0,d)@rotx(alpha)
    return M

def H_inv(H: Any) -> Array:

    R = H[:3, :3]
    d = H[:3, 3]
    es_simbolica = _usa_sympy(R, d)

    if es_simbolica:
        sp = _sympy()

        R = sp.Matrix(R)
        d = sp.Matrix(d).reshape(3, 1)

        Rt = R.T
        superior = Rt.row_join(-(Rt @ d))
        inferior = sp.Matrix([[0, 0, 0, 1]])

        Hi = superior.col_join(inferior)

    else:
        R = np.asarray(R, dtype=float)
        d = np.asarray(d, dtype=float).reshape(3, 1)

        Rt = R.T
        superior = np.hstack((Rt, -(Rt @ d)))
        inferior = np.array([[0, 0, 0, 1]])

        Hi = np.vstack((superior, inferior))

    return Hi

def Rot_Q(e1: float, e2: float, e3: float, e4: float) -> Array:
    """Devuelve una rotación 3x3 alrededor a partir de los componentes de un cuaternion."""
    filas = [
        [e1**2+e2**2-e3**2-e4**2, 2*(e2*e3+e1*e4), 2*(e2*e4-e1*e3)],
        [2*(e2*e3-e1*e4), e1**2-e2**2+e3**2-e4**2, 2*(e1*e2+e3*e4)],
        [2*(e1*e3+e2*e4), 2*(e3*e4-e1*e2), e1**2-e2**2-e3**2+e4**2],
    ]

    return _sympy().Matrix(filas) if _usa_sympy(e1, e2, e3, e4) else np.array(filas, dtype=float)

def Quaternions(H: Array) -> tuple[Any, Any, Any, Any]:

    R = H[:3,:3]
    trace = R[0, 0] + R[1, 1] + R[2, 2]

    
    e1 = (
        _sympy().sqrt((trace + 1) / 4)
        if _usa_sympy(H)
        else np.sqrt((trace + 1) / 4)
    )

    e2 = (R[1,2]-R[2,1])/(4*e1)
    e3 = (R[2,0]-R[0,2])/(4*e1)
    e4 = (R[0,1]-R[1,0])/(4*e1) 

    return e1, e2, e3, e4

def Axis2Quaternions(Lambda: Any, theta: float) -> tuple[Any, Any, Any, Any]:

    # Función que convierte los parámetros de Rodrigues (theta, lambda) a cuaterniones

    es_simbolica = _usa_sympy(*Lambda, theta)

    if es_simbolica:
        sp = _sympy()

        if isinstance(Lambda, sp.MatrixBase):

            componentes = list(Lambda)

        else:

            componentes = np.asarray(Lambda, dtype=object).reshape(-1).tolist()

        if len(componentes) != 3:

            raise ValueError("Lambda debe contener 3 elementos")

        l1, l2, l3, theta = (sp.sympify(valor) for valor in (*componentes, theta))

        c = sp.cos(theta / 2)
        s = sp.sin(theta / 2)

    else:
        componentes = np.asarray(Lambda, dtype=float).reshape(-1)

        if componentes.size != 3:
            raise ValueError("Lambda debe contener 3 elementos")

        l1, l2, l3 = (float(valor) for valor in componentes)

        c, s = _trig(float(theta) / 2)

    e1 = -c
    e2 = l1 * s
    e3 = l2 * s
    e4 = l3 * s

    return e1, e2, e3, e4

def derivada_numerica(q: float, t:float) -> Any:

    q = np.asarray(q, dtype=float).reshape(-1)
    t = np.asarray(t, dtype=float).reshape(-1)

    if q.size != t.size:
        raise ValueError("q y t deben tener la misma cantidad de muestras.")

    if t.size < 3:
        raise ValueError("Se necesitan al menos tres muestras.")


    qp = t * 0

    for x in range(1, len(t) - 1):

        qp[x] = (q[x] - q[x - 1]) / (t[x] - t[x - 1])

    qp[-1] = qp[-2]

    return qp

def derivada_numerica2(q: float, t:float) -> Any:

    q = np.asarray(q, dtype=float).reshape(-1)
    t = np.asarray(t, dtype=float).reshape(-1)

    if q.size != t.size:
        raise ValueError("q y t deben tener la misma cantidad de muestras.")

    if t.size < 3:
        raise ValueError("Se necesitan al menos tres muestras.")


    qp = t * 0

    for x in range(1, len(t) - 1):

        qp[x] = (q[x] - q[x - 1]) / (t[x] - t[x - 1])

    qp[-1] = qp[-2]
    qp[0] = qp[1]

    return qp

def derivada_numerica_central(q: float, t:float) -> Any:

    q = np.asarray(q, dtype=float).reshape(-1)
    t = np.asarray(t, dtype=float).reshape(-1)

    if q.size != t.size:
        raise ValueError("q y t deben tener la misma cantidad de muestras.")

    if t.size < 3:
        raise ValueError("Se necesitan al menos tres muestras.")


    qp = t * 0

    for x in range(1, len(t) - 1):

        qp[x] = (q[x+1] - q[x - 1]) / (t[x+1] - t[x - 1])

    qp[-1] = qp[-2]
    qp[0] = qp[1]

    return qp

def interpolacion_cubica(q_i: float, q_f: float, qp_i: float, qp_f: float, t_i: float, t_f: float, t: float) -> Any:

    
    t = np.asarray(t, dtype=float).reshape(-1)

    if t.size == 0:
   
        raise ValueError("El vector t no puede estar vacio")
   
    T = t_f - t_i

    if T == 0:
        raise ValueError("t_f y t_i no pueden ser iguales.")

    a = q_i
    b = qp_i

    c = (3 / T**2) * (q_f - q_i) - (2 / T**2) * qp_i - (1 / T**2) * qp_f
    d = (-2 /T**3) * (q_f - q_i) + (1/T**2) * (qp_i + qp_f)

    Q = a + b * (t - t_i) + c * (t - t_i)**2 + d * (t - t_i)**3

    return Q

def interpolacion_cubica_vector(q_i: float, q_f: float, qp_i: float, qp_f: float, t: float) -> tuple[np.ndarray, np.ndarray]:
    
    t = np.asarray(t, dtype=float).reshape(-1)

    if t.size == 0:
   
        raise ValueError("El vector t no puede estar vacio")

    t_i = t[0]
    t_f = t[-1]

    T = t_f - t_i

    if T == 0:
        raise ValueError("t_f y t_i no pueden ser iguales.")

    a = q_i
    b = qp_i

    c = (3 / T**2) * (q_f - q_i) - (2 / T**2) * qp_i - (1 / T**2) * qp_f
    d = (-2 /T**3) * (q_f - q_i) + (1/T**2) * (qp_i + qp_f)

    Q = np.zeros_like(t)

    for x in range(len(t)):

        Q[x] = a + b * (t[x] - t_i) + c * (t[x] - t_i)**2 + d * (t[x] - t_i)**3

    Qp = derivada_numerica(Q, t)

    return Q, Qp

def interpolacion_lineal(q_i: float, q_f: float, t_i: float, t_f: float, t: float) -> Any:

    t = np.asarray(t, dtype=float).reshape(-1)

    if t.size == 0:
        raise ValueError("El vector t no puede estar vacio")

    T = t_f - t_i

    if T == 0:
        raise ValueError("t_f y t_i no pueden ser iguales.")

    Q = (q_f - q_i) * (t - t_i ) / T + q_i

    return Q

def interpolacion_lineal_vector(q_i: float, q_f: float, t: float) -> tuple[np.ndarray, np.ndarray]:

    t = np.asarray(t, dtype=float).reshape(-1)

    if t.size < 2:
        raise ValueError("Se necesitan 2 muestras")

    t_i = t[0]
    t_f = t[-1]

    T = t_f - t_i

    if T == 0:
        raise ValueError("t_f y t_i no pueden ser iguales.")

    Q = np.zeros_like(t)

    for x in range(len(t)):

        Q[x] = (q_f-q_i)*(t[x]-t_i)/T+q_i

    Qp = derivada_numerica(Q, t)

    return Q, Qp

def interpolacion_tramos(q_i: float, q_f: float, Vmax: float, Amax: float, t:Any) -> Any:

    if Vmax <= 0 or Amax <= 0:
        raise ValueError("Vmax y Amax deben ser positivos")

    t = float(t)

    s = np.sign(q_f - q_i)

    Tau = Vmax / Amax

    T = s * (q_f - q_i)/ Vmax + Vmax / Amax

    if t <= Tau:

        Q = q_i + s * ((Amax / 2) * t**2)

    elif (T - Tau) <= t:

        Q = q_f + s * (-(Amax * T**2)/2 + Amax * T * t - (Amax/2) * t**2)

    else:

        Q  = (q_i - s * (Vmax**2/(2*Amax)) + s * Vmax * t)

    return Q

def interpolacion_tramos_vector(q_i: float, q_f: float, Vmax: float, Amax: float, t:Any) ->tuple[np.ndarray, np.ndarray]:

    t = np.asarray(t, dtype=float).reshape(-1)

    if t.size == 0:
        raise ValueError("El vector t no puede estar vacio")

    if Vmax <= 0 or Amax <= 0:
        raise ValueError("Vmax y Amax deben ser positivos")

    s = np.sign(q_f - q_i)

    Tau = Vmax / Amax

    T = s * (q_f - q_i)/ Vmax + Vmax / Amax

    Q = np.zeros_like(t)

    for x in range(len(t)):

        if t[x] <= Tau:

            Q[x] = q_i + s * ((Amax / 2) * t[x]**2)

        elif (T - Tau) <= t[x]:

            Q[x] = q_f + s * (-(Amax * T**2)/2 + Amax * T * t[x] - (Amax/2) * t[x]**2)

        else:

            Q[x] = (q_i - s * (Vmax**2/(2*Amax)) + s * Vmax * t[x])

    Qp = derivada_numerica(Q, t)

    return Q, Qp

def Energia_robot(qp: Any, tau: Any, t: Any) -> Any:

    # Función para calcular la energia del robot

    qp = np.asarray(qp, dtype=float)
    tau = np.asarray(tau, dtype=float)
    t = np.asarray(t, dtype=float).reshape(-1)

    if qp.ndim != 2:
        raise ValueError("qp debe ser una matriz bidimensional.")

    if tau.shape != qp.shape:
        raise ValueError("tau debe tener las mismas dimensiones que qp.")

    nmuestras, nsenales = qp.shape

    Energia = t * 0

    pt = qp[:, 0] * tau[:, 0]

    for nn in range(1, nsenales):

        pt = pt + qp[:, nn] * tau[:, nn]

    y1F = 0.0
    y1Fk1 = 0.0
    Tant = 0.0

    for k in range(nmuestras):

        Tf = t[k] - Tant
        Tant = t[k]

        y1F = Tf * pt[k] + y1Fk1
        y1Fk1 = y1F

        Energia[k] = y1F

    return Energia

def ejes(MatA: Any, t: float, *, ax: Any = None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    # Esta función se utiliza para calcular los extremos de los vectores
    # necesarios para dibujar un sistema coordenado relacionado con la matriz
    # de transformación homogénea MatA.

    MatA = np.asarray(MatA, dtype=float)

    if MatA.shape != (4, 4):
        raise ValueError("M debe ser una matriz de transformacion 4x4")

    po=MatA @ np.array([[0], [0], [0], [1]], dtype=float)
    px=MatA @ np.array([[t], [0], [0], [1]], dtype=float)
    py=MatA @ np.array([[0], [t], [0], [1]], dtype=float)
    pz=MatA @ np.array([[0], [0], [t], [1]], dtype=float)

    return po, px, py, pz

def christoffel(M: Any, q: Any, i: float, j: float, k: float) -> sp.Expr:

    # Función que calcula el símbolo de christoffel
    # Usa variables "sym"
     
    if M.rows != M.cols:
        raise ValueError("M debe ser una matriz cuadrada.")

    if q.rows != 1 and q.cols != 1:
        raise ValueError("q debe ser un vector de posiciones articulares.")

    if len(q) != M.rows:
        raise ValueError(
            "La longitud de q debe coincidir con las dimensiones de M."
        )

    n = M.rows

    if not all(1 <= indice <= n for indice in (i, j, k)):
        raise ValueError(
            f"Los índices i, j y k deben estar entre 1 y {n}."
        )

    # Conversión de índices MATLAB (base 1) a Python (base 0)
    i -= 1
    j -= 1
    k -= 1

    cijk = sp.Rational(1, 2) * (sp.diff(M[k, j], q[i]) + sp.diff(M[k, i], q[j]) - sp.diff(M[i, j], q[k]))
    
    return cijk

__all__ = [
    "rotx3", "roty3", "rotz3",
    "rotx", "roty", "rotz", "trans",
    "deg2rad", "rad2deg",
    "Rot_RPY", "Rot_RPY_grados", "RPY", "RPY_grados",
    "Rot_eje", "Eje_theta", "Eje_theta_grados",
    "DH", "H_inv",
    "Rot_Q", "Quaternions", "Axis2Quaternions",
    "derivada_numerica", "derivada_numerica2", "derivada_numerica_central",
    "interpolacion_cubica", "interpolacion_cubica_vector",
    "interpolacion_lineal", "interpolacion_lineal_vector",
    "interpolacion_tramos", "interpolacion_tramos_vector",
    "Energia_robot",
    "ejes",
    "christoffel"
]
