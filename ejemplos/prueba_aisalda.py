import numpy as np
import matplotlib.pyplot as plt
from SimpleRobotics import (
    interpolacion_cubica,
    interpolacion_cubica_vector,
)

# Parámetros idénticos a los de MATLAB
qi = 0.0
qf = 1.0
qpi = 1.0
qpf = 2.0

ti = 0.0
tf = 2.0

N = 101
t = np.linspace(ti, tf, N)

# 1. Evaluación escalar en cada instante
q_escalar = np.array([
    float(np.asarray(interpolacion_cubica(
        qi, qf, qpi, qpf, ti, tf, instante
    )).reshape(-1)[0])
    for instante in t
])

# 2. Evaluación de la función vectorial
q_vector, qp_vector = interpolacion_cubica_vector(
    qi, qf, qpi, qpf, t
)

q_vector = np.asarray(q_vector, dtype=float).reshape(-1)
qp_vector = np.asarray(qp_vector, dtype=float).reshape(-1)

# 3. Comprobar que las funciones de Python coinciden
print("--- Comparación entre funciones de Python ---")
print(
    "Máxima diferencia entre posiciones:",
    np.max(np.abs(q_escalar - q_vector))
)

# 4. Condiciones de frontera
print("\n--- Condiciones de frontera ---")
print(f"Posición inicial: calculada={q_escalar[0]:.10f}, "
      f"esperada={qi:.10f}")
print(f"Posición final:   calculada={q_escalar[-1]:.10f}, "
      f"esperada={qf:.10f}")
print(f"Velocidad inicial especificada: {qpi:.10f}")
print(f"Velocidad final especificada:   {qpf:.10f}")

# La velocidad de la función vectorial es una derivada numérica
# de Q según la implementación actual.
print(f"Velocidad vectorial inicial: {qp_vector[0]:.10f}")
print(f"Velocidad vectorial final:   {qp_vector[-1]:.10f}")

# 5. Exportar para comparar con MATLAB
datos = np.column_stack((t, q_escalar, q_vector, qp_vector))

np.savetxt(
    "resultados_python.csv",
    datos,
    delimiter=",",
    header="t,q_escalar,q_vector,qp_vector",
    comments="",
    fmt="%.12f",
)

# 6. Gráficas
fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax[0].plot(t, q_escalar, label="Interpolación escalar")
ax[0].plot(t, q_vector, "--", label="Interpolación vectorial")
ax[0].set_ylabel("Posición q")
ax[0].set_title("Interpolación cúbica de SimpleRobotics")
ax[0].grid(True)
ax[0].legend()

ax[1].plot(t, qp_vector, label="Velocidad vectorial")
ax[1].set_xlabel("Tiempo (s)")
ax[1].set_ylabel("Velocidad")
ax[1].grid(True)
ax[1].legend()

plt.tight_layout()
plt.savefig("comparacion_python.png", dpi=150)
plt.show()