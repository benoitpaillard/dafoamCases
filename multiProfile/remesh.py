import os, subprocess,glob

os.system("./Allclean.sh; rm -rf *.stl;~/Desktop/FreeCAD-0.21.2-Linux-x86_64.AppImage -c multiProfile.py; python3 ffdRead.py; python3 prePro.py")

os.system("docker run -it --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '. /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v1812/etc/bashrc && . /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun -np 4 /home/dafoamuser/dafoam/packages/miniconda3/bin/python runScript_anyElements.py'")

nElements=len(glob.glob('profile*.stl'))

for ii in range(10):

	os.system('reconstructPar')

	os.system("surfaceMeshExtract mep.stl -patches '(\"profile.*\")'")

	tiime=subprocess.getoutput('foamListTimes').split()[-1]

	os.system("rm -rf iter"+str(ii)+";mkdir iter"+str(ii)+";mv mep* iter"+str(ii))

	os.system("cp iter"+str(ii)+"/mep_"+tiime+".stl mep.stl")

	os.system("./Allclean.sh; python3 ffdRead.py; python3 prePro.py; mv deformedFFD.xyz FFD/wing.xyz")

	os.system("docker run -it --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '. /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v1812/etc/bashrc && . /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun -np 4 /home/dafoamuser/dafoam/packages/miniconda3/bin/python runScript_anyElements.py'")
