from foamlib import FoamCase
import numpy,os,glob

os.system('surfaceGenerateBoundingBox mep.stl box.stl 10 10 10 10 0 0')

os.system('head -n -32 box.stl > temp.stl && mv temp.stl box.stl')

os.system('cp system/meshDict.org system/meshDict')

nElements=len(glob.glob('profile*.stl'))

case = FoamCase('.')
with case.file('system/meshDict') as f:
	for ii in range(nElements):
		LEcons=numpy.loadtxt('LEconsProfile'+str(ii))
		f['objectRefinements']['LEProfile'+str(ii)+'Fine']={'type':'cone','cellSize':'$refFine','radius0':'$widthFine','radius1':'$widthFine','p0':LEcons,'p1':[LEcons[0],LEcons[1],1]}
		f['objectRefinements']['LEProfile'+str(ii)+'Normal']={'type':'cone','cellSize':'$refNormal','radius0':'$widthNormal','radius1':'$widthNormal','p0':LEcons,'p1':[LEcons[0],LEcons[1],1]}
		TEcons=numpy.loadtxt('TEconsProfile'+str(ii))
		f['objectRefinements']['TEProfile'+str(ii)+'Fine']={'type':'cone','cellSize':'$refFine','radius0':'$widthFine','radius1':'$widthFine','p0':TEcons,'p1':[TEcons[0],TEcons[1],1]}
		f['objectRefinements']['TEProfile'+str(ii)+'Normal']={'type':'cone','cellSize':'$refNormal','radius0':'$widthNormal','radius1':'$widthNormal','p0':TEcons,'p1':[TEcons[0],TEcons[1],1]}
		f['renameBoundary']['newPatchNames']['profile'+str(ii)]={'type':'wall','newName':'profile'+str(ii)}
	
os.system('export OMP_NUM_THREADS=2 && cartesian2DMesh')

os.system('renumberMesh -overwrite')

os.system('checkMesh')

os.system('cp -r 0.orig 0')
