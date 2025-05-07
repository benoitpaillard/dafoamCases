#!/usr/bin/env python
"""
DAFoam run script for the NACA0012 airfoil at low-speed
"""

# =============================================================================
# Imports
# =============================================================================
import os,glob
import argparse
import numpy as np
import json
from mpi4py import MPI
import openmdao.api as om
from pyspline import Curve
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils


parser = argparse.ArgumentParser()
# which optimizer to use. Options are: IPOPT (default), SLSQP, and SNOPT
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
# which task to run. Options are: opt (default), runPrimal, runAdjoint, checkTotals
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()


profiles=['profile'+str(i) for i in range(len(glob.glob('profile*.stl')))]
# =============================================================================
# Input Parameters
# =============================================================================
U0 = 5.0
p0 = 0.0
nuTilda0 = 4.5e-5#nu*4.349*(turbl)**0.25
CL_target = 3.5
aoa0 = 0
#A0 = 1*(1+0.5+0.5)
A0 = .1*(len(profiles))
# rho is used for normalizing CD and CL
rho0 = 1.0

# Input parameters for DAFoam
daOptions = {
#"writeDeformedFFDs": True,
    "designSurfaces": profiles,
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-4,
#    "printInterval":10,
#    "writeMinorIterations":True,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": profiles,
            "directionMode": "parallelToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": profiles,
            "directionMode": "normalToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
        "skewness": {
            "type": "meshQualityKS",
            "source": "allCells",
            "coeffKS": 20.0,
            "metric": "faceSkewness",
            "scale": 1.0,
        },
        "nonOrtho": {
            "type": "meshQualityKS",
            "source": "allCells",
            "coeffKS": 1.0,
            "metric": "nonOrthoAngle",
            "scale": 1.0,
        },
    },
    "adjEqnOption": {
    "gmresRelTol": 1.0e-6,
#"gmresRelTol": 1e-4,
     "pcFillLevel": 1, 
#          "pcFillLevel": 2, 
     "jacMatReOrdering": "rcm",
     "gmresMaxIters": 2000, "gmresRestart": 2000
     },
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "nuTilda": nuTilda0 * 10.0,
        "phi": 1.0,
    },
    "checkMeshThreshold": {"maxAspectRatio": 500000.0, "maxNonOrth": 89.9, "maxSkewness": 30.0},
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {
            "type": "patchVelocity",
            "patches": ["inout"],
            "flowAxis": "x",
            "normalAxis": "y",
            "components": ["solver", "function"],
        },
    },
}

# Mesh deformation setup
meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    # point and normal for the symmetry plane
    "symmetryPlanes": [[[0, 0, 0], [0, 0, .1]], [[0, 0, .1], [0, 0, .1]]],
}


# Top class to setup the optimization problem
class Top(Multipoint):
    def setup(self):

        # create the builder to initialize the DASolvers
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)

        # add the design variable component to keep the top level design variables
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        # add the mesh component
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())

        # add the geometry component (FFD)
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wing.xyz", type="ffd"))

        # add a scenario (flow condition) for optimization, we pass the builder
        # to the scenario to actually run the flow and adjoint
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))

        # need to manually connect the x_aero0 between the mesh and geometry components
        # here x_aero0 means the surface coordinates of structurally undeformed mesh
        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        # need to manually connect the x_aero0 between the geometry component and the scenario1
        # scenario group
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):

        # get the surface coordinates from the mesh component
        points = self.mesh.mphys_get_surface_mesh()

        # add pointset to the geometry component
        self.geometry.nom_add_discipline_coords("aero", points)

        # set the triangular points to the geometry component for geometric constraints
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        # Create reference axis for the twist variables
        for ii in range(len(profiles)):
            leListFlap = np.loadtxt('LEconsProfile'+str(ii))
            leListFlap = np.vstack((leListFlap,leListFlap))
            xFlap = leListFlap[:,0]
            yFlap = leListFlap[:,1]
            zFlap = [0, .1]
            cFlap = Curve(x=xFlap, y=yFlap, z=zFlap, k=2)
            # Note here we set raySize=5 to avoid the warning when having highly skewed FFDs
            # "ray might not have been longenough to intersect the nearest curve."
            self.geometry.nom_addRefAxis(name="Axis"+str(ii), curve=cFlap, axis="z", volumes=[ii], raySize=5)
            def translateVar(axis):
                def translateflap(val, geo):
                    C = geo.extractCoef(axis)
                    dx = val[0]
                    dy = val[1]
                    for i in range(len(C)):
                        C[i, 0] = C[i, 0] + dx
                    for i in range(len(C)):
                        C[i, 1] = C[i, 1] + dy
                    geo.restoreCoef(C, axis)
                return translateflap
            # add the global shape variable
            self.geometry.nom_addGlobalDV(dvName="translate"+str(ii), value=np.zeros(2), func=translateVar('Axis'+str(ii)))
            self.dvs.add_output("translate"+str(ii), val=np.zeros(2))
            self.connect("translate"+str(ii), "geometry.translate"+str(ii))

            def twistVar(axis):
                def twistflap(val, geo):
                    for i in range(2):
                        geo.rot_z[axis].coef[i] = -val[0]
                return twistflap
                
            self.geometry.nom_addGlobalDV(dvName="twist"+str(ii), value=[0.0], func=twistVar('Axis'+str(ii)))

            self.dvs.add_output("twist"+str(ii), val=np.array([0.0]))

            self.connect("twist"+str(ii), "geometry.twist"+str(ii))
        
        pts = []
        shapes=[[]]*len(profiles)
        
        # use the shape function to define shape variables for 2D airfoil
#        pts.append(self.geometry.DVGeo.getLocalIndex(0))
        dir_x = np.array([1.0, 0.0, 0.0])
        dir_y = np.array([0.0, 1.0, 0.0])
#        for i in range(pts[0].shape[0]):
#            for j in range(pts[0].shape[1]):
#                # k=0 and k=1 move together to ensure symmetry
#                shapes[0].append({pts[0][i, j, 0]: dir_y, pts[0][i, j, 1]: dir_y})
#    
#        self.geometry.nom_addShapeFunctionDV(dvName="shape"+str(0), shapes=shapes[0])
#        
#        for ii in range(len(profiles)):
            # use the shape function to define shape variables for 2D airfoil
#            pts.append(self.geometry.DVGeo.getLocalIndex(ii))
#            dir_y = np.array([0.0, 1.0, 0.0])
#            for i in range(pts[ii].shape[0]):
#                for j in range(pts[ii].shape[1]):
#                    # k=0 and k=1 move together to ensure symmetry
#                    shapes[ii].append({pts[ii][i, j, 0]: dir_y, pts[ii][i, j, 1]: dir_y})
#            # LE/TE shape, the j=0 and j=1 move in opposite directions so that
#            # the LE/TE are fixed
#            for i in [0, pts[ii].shape[0] - 1]:
#                shapes[ii].append({pts[ii][i, 0, 0]: dir_y, pts[ii][i, 0, 1]: dir_y, pts[ii][i, 1, 0]: -dir_y, pts[ii][i, 1, 1]: -dir_y})
#            self.geometry.nom_addShapeFunctionDV(dvName="shape"+str(ii), shapes=shapes[ii])
            
            # setup the symmetry constraint to link the y displacement between j=0 and j=1 (constant thickness)
#            for i in range(pts[ii].shape[0]):
#                for j in range(pts[ii].shape[1]):
#                    # k=0 and k=1 move together to ensure symmetry
#                    shapes[ii].append({pts[ii][i, 0, 0]: dir_y, pts[ii][i, 1, 0]: dir_y})
            
#####         setup the symmetry for forward foil
        pts0=self.geometry.DVGeo.getLocalIndex(0)
        shapes0 = []
        for i in range(int(pts0.shape[0]/2)):
            for j in range(pts0.shape[1]):
                # k=0 and k=1 move together to ensure symmetry
                shapes0.append({pts0[i, j, 0]: dir_y, pts0[-i-1, j, 0]: dir_y, pts0[i, j, 1]: dir_y, pts0[-i-1, j, 1]: dir_y})
                
        pts1=self.geometry.DVGeo.getLocalIndex(1)
        shapes1 = []
        for i in range(1,pts1.shape[0]-1):
#            for j in range(pts1.shape[1]):
                # k=0 and k=1 move together to ensure symmetry
#                shapes1.append({pts1[i, j, 0]: dir_x, pts1[i, j, 1]: dir_x})
                shapes1.append({pts1[i, 0, 0]: dir_x, pts1[i, 0, 1]: dir_x, pts1[i, 1, 0]: dir_x, pts1[i, 1, 1]: dir_x})
        
        print(shapes0)
        print(shapes1)
        
#        for ii in range(len(profiles)):    
        self.geometry.nom_addShapeFunctionDV(dvName="shape0", shapes=shapes0)
        self.dvs.add_output("shape0", val=np.array([0] * len(shapes0)))
        self.connect("shape0", "geometry.shape0")
        
        self.geometry.nom_addShapeFunctionDV(dvName="shape1", shapes=shapes1)
        self.dvs.add_output("shape1", val=np.array([0] * len(shapes1)))
        self.connect("shape1", "geometry.shape1")
            
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        # manually connect the dvs output to the geometry and scenario1
        self.connect("patchV", "scenario1.patchV")

    ###         setup the thickness constraints
#            leList.append(np.loadtxt('LEconsProfile'+str(ii)))
#            leList[ii] = np.vstack((leList[ii],leList[ii]))
#            leList[ii][0,-1]=1e-4
#            leList[ii][1,-1]=.1-1e-4
#            teList.append(np.loadtxt('TEconsProfile'+str(ii)))
#            teList[ii] = np.vstack((teList[ii],teList[ii]))
#            teList[ii][0,-1]=1e-4
#            teList[ii][1,-1]=.1-1e-4
#            self.geometry.nom_addThicknessConstraints2D("thickcon"+str(ii), leList[ii], teList[ii], nSpan=2, nChord=10)
#                            ###         setup the volume constraints
#            self.geometry.nom_addVolumeConstraint("volcon"+str(ii), leList[ii], teList[ii], nSpan=2, nChord=10)

########################

        # define the design variables to the top level
        for ii in range(len(profiles)):
            self.add_design_var("shape"+str(ii), lower=-.05, upper=.05, scaler=1)
#            self.add_constraint("geometry.thickcon"+str(ii), lower=1, upper=1, scaler=1.0)
#            self.add_constraint("geometry.linearcon"+str(ii), equals=0.0, scaler=1.0, linear=True)
#            self.add_constraint("geometry.linearcon2"+str(ii), equals=0.0, scaler=1.0, linear=True)
        
        self.add_design_var("translate1", lower=[-0.05, -0.05], upper=[0.05, 0.05], scaler=1.0)
        self.add_design_var("twist1", lower=-1.0, upper=1.0, scaler=1.0)
#        self.add_constraint("geometry.linearcon30", equals=0.0, scaler=1.0, linear=True)
#            self.add_constraint("geometry.volcon"+str(ii), lower=1.0, scaler=1.0)
        
        # here we fix the U0 magnitude and allows the aoa to change
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=1)

        # add objective and constraints to the top level
        self.add_objective("scenario1.aero_post.CL", scaler=-1.0)
#        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
#        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
#        self.add_constraint("scenario1.aero_post.CL", lower=CL_target, scaler=1.0)
        self.add_constraint("scenario1.aero_post.skewness", upper=6.0, scaler=1.0)
        self.add_constraint("scenario1.aero_post.nonOrtho", upper=70.0, scaler=1.0)


# OpenMDAO setup
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
om.n2(prob, show_browser=False, outfile="mphys.html")

# initialize the optimization function
optFuncs = OptFuncs(daOptions, prob)

# use pyoptsparse to setup optimization
prob.driver = om.pyOptSparseDriver()
prob.driver.options["optimizer"] = args.optimizer
# options for optimizers
#if args.optimizer == "SNOPT":
#    prob.driver.opt_settings = {
#        "Major feasibility tolerance": 1.0e-5,
#        "Major optimality tolerance": 1.0e-5,
#        "Minor feasibility tolerance": 1.0e-5,
#        "Verify level": -1,
#        "Function precision": 1.0e-5,
#        "Major iterations limit": 3,
#        "Nonderivative linesearch": None,
#        "Print file": "opt_SNOPT_print.txt",
#        "Summary file": "opt_SNOPT_summary.txt",
#    }
if args.optimizer == "IPOPT":
    prob.driver.opt_settings = {
        "tol": 1.0e-5,
        "constr_viol_tol": 1.0e-5,
        "max_iter": 30,#10,# for cl opt 3
        "print_level": 5,
        "output_file": "opt_IPOPT.txt",
        "mu_strategy": "adaptive",
        "limited_memory_max_history": 10,
        "nlp_scaling_method": "none",
        "alpha_for_y": "full",
        "recalc_y": "yes",
    }
#elif args.optimizer == "SLSQP":
#    prob.driver.opt_settings = {
#        "ACC": 1.0e-5,
#        "MAXIT": 100,
#        "IFILE": "opt_SLSQP.txt",
#    }
else:
    print("optimizer arg not valid!")
    exit(1)

prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
prob.driver.options["print_opt_prob"] = True
prob.driver.hist_file = "OptView.hst"

if args.task == "run_driver":
    # solve CL
#    optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[CL_target], designVarsComp=[1])
    # run the optimization
    prob.run_driver()
    prob.model.geometry.DVGeo.writeTecplot("deformedFFD.dat")
    prob.model.geometry.DVGeo.writePlot3d("deformedFFD.xyz")
    # write the optimal design variable values to disk
    OptDesignVars = {var: val.tolist() for var, val in prob.model.geometry.DVGeo.getValues().items()}
    with open('OptDesignVars.json', 'w') as f:
        json.dump(OptDesignVars, f, indent=4)
elif args.task == "run_model":
    # just run the primal once
    prob.run_model()
elif args.task == "compute_totals":
    # just run the primal and adjoint once
    prob.run_model()
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
elif args.task == "check_totals":
    # verify the total derivatives against the finite-difference
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
else:
    print("task arg not found!")
    exit(1)
