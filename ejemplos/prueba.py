
import matplotlib.pyplot as plt
import SimpleRobotics as rt
from numpy import pi
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

t = 0.1
tf = 14
cr = "k"
ar = 2

H00 = rt.Sistema3Dbool(np.eye(4), t, "x_0", "y_0", "z_0",[True, False, True], tf, ax=ax)

H01 = rt.DH(rt.deg2rad(180), 0.2, 0, pi/2)


"""po0 = rt.Sistema3D(H00, t, "x_0", "y_0", "z_0", tf, ax = ax)"""

po1 = rt.Sistema3D(H01, t, "x_1", "y_1", "z_1", tf, ax=ax)
linea = rt.eslabon(H00, po1, cr, ar, ax=ax)



ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

ax.set_xlim(-0.5, 0.5)
ax.set_ylim(-0.5, 0.5)
ax.set_zlim(-0.5, 0.5)
ax.set_box_aspect((1,1,1))

plt.show()

print(5**2)