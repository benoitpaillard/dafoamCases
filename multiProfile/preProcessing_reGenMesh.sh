#!/bin/bash

 ./Allclean.sh
# generate mesh
echo "Generating mesh.."
~/Desktop/FreeCAD-0.21.2-Linux-x86_64.AppImage -c multiProfile.py 

blockMesh &> logMeshGeneration.txt
surfaceFeatureExtract >> logMeshGeneration.txt
snappyHexMesh -overwrite >> logMeshGeneration.txt
extrudeMesh >> logMeshGeneration.txt
transformPoints -scale '(1 1 0.1)' >> logMeshGeneration.txt
createPatch -overwrite >> logMeshGeneration.txt
renumberMesh -overwrite >> logMeshGeneration.txt
echo "Generating mesh.. Done!"

# copy initial and boundary condition files
cp -r 0.orig 0
