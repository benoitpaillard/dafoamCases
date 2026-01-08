import os, subprocess,glob

os.system("./Allclean.sh; rm -rf *.stl iter*;~/FreeCAD*.AppImage -c multiProfile.py; python3 ffdRead.py; python3 prePro.py")

os.system('rm -rf results;mkdir results')

for ii in range(1):

	os.system("docker run --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v4.0.3 bash -c '. /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v1812/etc/bashrc && . /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun -np 8 /home/dafoamuser/dafoam/packages/miniconda3/bin/python runScript_anyElements.py 2>&1 | tee logOpt"+str(ii)+".txt'")

#	os.system('reconstructPar')

#	os.system("surfaceMeshExtract mep.stl -patches '(\"profile.*\")'")

#	tiime=subprocess.getoutput('foamListTimes').split()[-1]

#	os.system('cp mep_'+tiime+'.stl results/mep'+str(ii)+'.stl')
#	os.system('cp deformedFFD.dat results/deformedFFD'+str(ii)+'.dat')
#	os.system('cp OptDesignVars.json results/OptDesignVars'+str(ii)+'.json')
#	
#	os.system("rm -rf iter"+str(ii)+";mkdir iter"+str(ii)+";mv mep* opt_IPOPT.txt 0 0.0* {1..9}* logOpt"+str(ii)+".txt iter"+str(ii)+";cp -r constant system paraview.foam iter"+str(ii))
#	
#	os.system("cp iter"+str(ii)+"/mep_"+tiime+".stl mep.stl")

#	os.system("./Allclean.sh; python3 ffdRead.py; python3 prePro.py; mv deformedFFD.xyz FFD/wing.xyz")

