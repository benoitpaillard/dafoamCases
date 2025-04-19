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
parser.add_argument("-task", help="type of run to do", type=str, default="opt")
args = parser.parse_args()


profiles=['profile'+str(i) for i in range(len(glob.glob('profile*.stl')))]
# =============================================================================
# Input Parameters
# =============================================================================
U0 = 5.0
p0 = 0.0
nuTilda0 = 4.5e-5#nu*4.349*(turbl)**0.25
CL_target = 2.5
aoa0 = 0
#A0 = 1*(1+0.5+0.5)
A0 = .1*2.1#(len(profiles))
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
    "objFunc": {
        "CD": {
            "part1": {
                "type": "force",
                "source": "patchToFace",
                "patches": profiles,
                "directionMode": "parallelToFlow",
                "alphaName": "aoa",
                "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
                "addToAdjoint": True,
            }
        },
        "CL": {
            "part1": {
                "type": "force",
                "source": "patchToFace",
                "patches": profiles,
                "directionMode": "normalToFlow",
                "alphaName": "aoa",
                "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
                "addToAdjoint": True,
            }
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
    "designVar": {
        "aoa": {"designVarType": "AOA", "patches": ["inout"], "flowAxis": "x", "normalAxis": "y"},
    },
"checkMeshThreshold": {"maxAspectRatio": 500000.0, "maxNonOrth": 89.9, "maxSkewness": 30.0},
}

daOptions['designVar']["translate0"]= {"designVarType": "FFD"}
daOptions['designVar']["twist0"]= {"designVarType": "FFD"}
daOptions['designVar']["translate2"]= {"designVarType": "FFD"}
daOptions['designVar']["twist2"]= {"designVarType": "FFD"}

for ii in range(len(profiles)):
    daOptions['designVar']["shape"+str(ii)]= {"designVarType": "FFD"}

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
        self.mphys_add_scenario("cruise", ScenarioAerodynamic(aero_builder=dafoam_builder))

        # need to manually connect the x_aero0 between the mesh and geometry components
        # here x_aero0 means the surface coordinates of structurally undeformed mesh
        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        # need to manually connect the x_aero0 between the geometry component and the cruise
        # scenario group
        self.connect("geometry.x_aero0", "cruise.x_aero")

    def configure(self):
        # configure and setup perform a similar function, i.e., initialize the optimization.
        # But configure will be run after setup

        # add the objective function to the cruise scenario
        self.cruise.aero_post.mphys_add_funcs()

        # get the surface coordinates from the mesh component
        points = self.mesh.mphys_get_surface_mesh()

        # add pointset to the geometry component
        self.geometry.nom_add_discipline_coords("aero", points)

        # set the triangular points to the geometry component for geometric constraints
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        # define an angle of attack function to change the U direction at the far field
        def aoa(val, DASolver):
            print('TRYING AOA = '+str(val))
            aoa = val[0] * np.pi / 180.0
            U = [float(U0 * np.cos(aoa)), float(U0 * np.sin(aoa)), 0]
            # we need to update the U value only
            DASolver.setOption("primalBC", {"U0": {"value": U}})
            DASolver.updateDAOption()

        # pass this aoa function to the cruise group
        self.cruise.coupling.solver.add_dv_func("aoa", aoa)
        self.cruise.aero_post.add_dv_func("aoa", aoa)
        self.dvs.add_output("aoa", val=np.array([aoa0]))
        self.connect("aoa", "cruise.aoa")
        
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
        
        pts=[]
        nShapes=[]
        indSetA = []
        indSetB = []
        indSetA2 = []
        indSetB2 = []
        indSetA3 = []
        indSetB3 = []
        indSetA4 = []
        indSetB4 = []
        leList=[]
        teList=[]
        for ii in range(len(profiles)):
            # select the FFD points to move
            pts.append(self.geometry.DVGeo.getLocalIndex(ii))
            if ii==0:
        	    nShapes.append(self.geometry.nom_addLocalDV(dvName="shape"+str(ii), axis='y', pointSelect=geo_utils.PointSelect("list", pts[ii][:, :, :].flatten())))
            elif ii==1:
                nShapes.append(self.geometry.nom_addLocalDV(dvName="shape"+str(ii), axis='y', pointSelect=geo_utils.PointSelect("list", pts[ii][:, :, :].flatten())))
            elif ii==2:
                nShapes.append(self.geometry.nom_addLocalDV(dvName="shape"+str(ii), axis='y', pointSelect=geo_utils.PointSelect("list", pts[ii][:-1, :, :].flatten())))
            else:
                nShapes.append(self.geometry.nom_addLocalDV(dvName="shape"+str(ii), axis='x', pointSelect=geo_utils.PointSelect("list", pts[ii][:, :, :].flatten())))
            #            # add the design variables to the dvs component's output
            self.dvs.add_output("shape"+str(ii), val=np.array([0] * nShapes[ii]))
            # manually connect the dvs output to the geometry and cruise
            self.connect("shape"+str(ii), "geometry.shape"+str(ii))
            # setup the symmetry constraint to link the y displacement between k=0 and k=1
            indSetA.append([])
            indSetB.append([])
            if ii==1:
                for i in range(pts[ii].shape[0]):
                    for j in range(pts[ii].shape[1]):
                        indSetA[ii].append(pts[ii][i, j, 0])
                        indSetB[ii].append(pts[ii][i, j, 1])
                self.geometry.nom_addLinearConstraintsShape("linearcon"+str(ii), indSetA[ii], indSetB[ii], factorA=1.0, factorB=-1.0)
            else:
                for i in range(pts[ii].shape[0]-1):
                    for j in range(pts[ii].shape[1]):
                        indSetA[ii].append(pts[ii][i, j, 0])
                        indSetB[ii].append(pts[ii][i, j, 1])
                self.geometry.nom_addLinearConstraintsShape("linearcon"+str(ii), indSetA[ii], indSetB[ii], factorA=1.0, factorB=-1.0)
            # setup the symmetry constraint to link the y displacement between j=0 and j=1 (constant thickness)
            indSetA2.append([])
            indSetB2.append([])
            if ii==1:
                for i in range(pts[ii].shape[0]):
                    indSetA2[ii].append(pts[ii][i, 0, 0])
                    indSetB2[ii].append(pts[ii][i, 1, 0])
                self.geometry.nom_addLinearConstraintsShape("linearcon2"+str(ii), indSetA2[ii], indSetB2[ii], factorA=1.0, factorB=-1.0)
            else:
                for i in range(pts[ii].shape[0]-1):
                    indSetA2[ii].append(pts[ii][i, 0, 0])
                    indSetB2[ii].append(pts[ii][i, 1, 0])
                self.geometry.nom_addLinearConstraintsShape("linearcon2"+str(ii), indSetA2[ii], indSetB2[ii], factorA=1.0, factorB=-1.0)
        # setup the symmetry for main foil
        indSetA3.append([])
        indSetB3.append([])
        for i in range(int(pts[1].shape[0]/2)):
            for j in range(pts[1].shape[1]):
                indSetA3[0].append(pts[1][i, j, 0])
                indSetB3[0].append(pts[1][-i-1, j, 0])
        self.geometry.nom_addLinearConstraintsShape("linearcon3"+str(1), indSetA3[0], indSetB3[0], factorA=1.0, factorB=-1.0)
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
        self.add_design_var("aoa", lower=-5, upper=5, scaler=1.0)
        for ii in range(len(profiles)):
            self.add_design_var("shape"+str(ii), lower=-.01, upper=.01, scaler=3.0)
#            self.add_constraint("geometry.thickcon"+str(ii), lower=1, upper=1, scaler=1.0)
            self.add_constraint("geometry.linearcon"+str(ii), equals=0.0, scaler=1.0, linear=True)
            self.add_constraint("geometry.linearcon2"+str(ii), equals=0.0, scaler=1.0, linear=True)
        
        self.add_design_var("translate0", lower=[-0.05, -0.05], upper=[0.05, 0.05], scaler=1.0)
        self.add_design_var("twist0", lower=-1.0, upper=1.0, scaler=1.0)
        self.add_design_var("translate2", lower=[-0.05, -0.05], upper=[0.05, 0.05], scaler=1.0)
        self.add_design_var("twist2", lower=-1.0, upper=1.0, scaler=1.0)
        self.add_constraint("geometry.linearcon31", equals=0.0, scaler=1.0, linear=True)
#            self.add_constraint("geometry.volcon"+str(ii), lower=1.0, scaler=1.0)
        
        # add objective and constraints to the top level
        self.add_objective("cruise.aero_post.CL", scaler=-1.0)
#        self.add_objective("cruise.aero_post.CD", scaler=1.0)
#        self.add_constraint("cruise.aero_post.CL", equals=CL_target, scaler=3.0)


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
        "max_iter": 10,# for cl opt 3
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

if args.task == "opt":
    # solve CL
#    optFuncs.findFeasibleDesign(["cruise.aero_post.CL"], ["aoa"], targets=[2.358723274428963])
    # run the optimization
    prob.run_driver()
    prob.model.geometry.DVGeo.writeTecplot("deformedFFD.dat")
    prob.model.geometry.DVGeo.writePlot3d("deformedFFD.xyz")
    # write the optimal design variable values to disk
    OptDesignVars = {var: val.tolist() for var, val in prob.model.geometry.DVGeo.getValues().items()}
    with open('OptDesignVars.json', 'w') as f:
        json.dump(OptDesignVars, f, indent=4)
elif args.task == "runPrimal":
    # just run the primal once
    prob.run_model()
elif args.task == "runAdjoint":
    # just run the primal and adjoint once
    prob.run_model()
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
elif args.task == "checkTotals":
    # verify the total derivatives against the finite-difference
    prob.run_model()
    prob.check_totals(
        of=["cruise.aero_post.CD", "cruise.aero_post.CL"], wrt=["shape", "aoa"], compact_print=True, step=1e-3, form="central", step_calc="abs"
    )
else:
    print("task arg not found!")
    exit(1)
