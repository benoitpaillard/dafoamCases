#!/bin/bash

# clean everyting
echo "Cleaning..."
rm -rf 0
rm -rf postProcessing
rm -rf constant/extendedFeatureEdgeMesh
rm -rf constant/triSurface
#            rm -rf constant/polyMesh/
rm -rf *.bin *.info
#rm -rf *.dat *.xyz
rm -rf processor* 0.00*
rm -rf {1..9}*
exit
