from foamlib import FoamCase
import numpy,os

os.system('surfaceGenerateBoundingBox mep.stl box.stl 10 10 10 10 0 0')

os.system('head -n -32 box.stl > temp.stl && mv temp.stl box.stl')

os.system('cp system/meshDict.org system/meshDict')

case = FoamCase('.')
with case.file('system/meshDict') as f:
#	LEconsSlat=numpy.loadtxt('LEconsSlat')
#	f['objectRefinements']['LESlat']['p0']=LEconsSlat
#	f['objectRefinements']['LESlat']['p1']=[LEconsSlat[0],LEconsSlat[1],1]
#	TEconsSlat=numpy.loadtxt('TEconsSlat')
#	f['objectRefinements']['TESlat']['p0']=TEconsSlat
#	f['objectRefinements']['TESlat']['p1']=[TEconsSlat[0],TEconsSlat[1],1]
	LEconsMain=numpy.loadtxt('LEconsMain')
	f['objectRefinements']['LEMainFine']['p0']=LEconsMain
	f['objectRefinements']['LEMainFine']['p1']=[LEconsMain[0],LEconsMain[1],1]
	f['objectRefinements']['LEMain']['p0']=LEconsMain
	f['objectRefinements']['LEMain']['p1']=[LEconsMain[0],LEconsMain[1],1]
	TEconsMain=numpy.loadtxt('TEconsMain')
	f['objectRefinements']['TEMainFine']['p0']=TEconsMain
	f['objectRefinements']['TEMainFine']['p1']=[TEconsMain[0],TEconsMain[1],1]
	f['objectRefinements']['TEMain']['p0']=TEconsMain
	f['objectRefinements']['TEMain']['p1']=[TEconsMain[0],TEconsMain[1],1]
	LEconsFlap=numpy.loadtxt('LEconsFlap')
	f['objectRefinements']['LEFlapFine']['p0']=LEconsFlap
	f['objectRefinements']['LEFlapFine']['p1']=[LEconsFlap[0],LEconsFlap[1],1]
	f['objectRefinements']['LEFlap']['p0']=LEconsFlap
	f['objectRefinements']['LEFlap']['p1']=[LEconsFlap[0],LEconsFlap[1],1]
	TEconsFlap=numpy.loadtxt('TEconsFlap')
	f['objectRefinements']['TEFlapFine']['p0']=TEconsFlap
	f['objectRefinements']['TEFlapFine']['p1']=[TEconsFlap[0],TEconsFlap[1],1]
	f['objectRefinements']['TEFlap']['p0']=TEconsFlap
	f['objectRefinements']['TEFlap']['p1']=[TEconsFlap[0],TEconsFlap[1],1]


os.system('export OMP_NUM_THREADS=2 && cartesian2DMesh')

os.system('renumberMesh -overwrite')

os.system('checkMesh')

os.system('cp -r 0.orig 0')
