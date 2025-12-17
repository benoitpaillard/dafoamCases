#!/usr/bin/env python
"""
DAFoam run script for the NACA0012 airfoil at low-speed (unsteady)
"""

# =============================================================================
# Imports
# =============================================================================
import os,glob
from mpi4py import MPI
from dafoam import PYDAFOAM
import numpy as np

profiles=['profile'+str(i) for i in range(len(glob.glob('profile*.stl')))]

# =============================================================================
# Input Parameters
# =============================================================================
gcomm = MPI.COMM_WORLD

U0 = 20.0
A0 = 0.1
aoa0 = 20.0
Ux = float(U0 * np.cos(aoa0 * np.pi / 180.0))
Uy = float(U0 * np.sin(aoa0 * np.pi / 180.0))

# Set the parameters for optimization
daOptions = {
    "designSurfaces": profiles,
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-16,
    "primalMinResTolDiff": 1.0e16,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [Ux, Uy, 0.0]},
        "useWallFunction": False,
    },
    "checkMeshThreshold": {"maxAspectRatio": 5000.0},
}

DASolver = PYDAFOAM(options=daOptions, comm=gcomm)
DASolver()
