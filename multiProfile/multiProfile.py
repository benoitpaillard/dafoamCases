import Part, FreeCAD, math, Draft,os,numpy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')

if os.path.exists('box'):os.remove('box')

#rotations=[0,-30]
#translations=[[0,0],[1,-.05]]
#rotations=[0,-10,-20]
#translations=[[0,0],[1,-.05],[1.95,-.5]]
rotations=[0,-10,-20,-30]
translations=[[0,0],[1,-.05],[1.95,-.5],[2.95,-1]]

##Generating profile
os.system('xfoil << EOF\n naca9301\n gdes \n tgap 0.001\n0.3\n \npcop\n psav profile \n quit \n EOF')#before tgap 0.015
profile=list(numpy.loadtxt('profile'))
profileWire0=Part.makePolygon([Base.Vector(*x) for x in profile+[profile[0]]])

profileWire=[profileWire0.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), rotations[ii]).scale(1).translate(Base.Vector(*translations[ii])) for ii in range(len(rotations))]
profileExtrude=[xx.extrude(Base.Vector(0,0,.1)) for xx in profileWire]
[profileExtrude[ii].exportStl('profile'+str(ii)+'.stl') for ii in range(len(rotations))]
[os.system('sed -i -e \'s#solid#solid profile'+str(ii)+'#g\' profile'+str(ii)+'.stl') for ii in range(len(rotations))]

os.system('cat '+(' ').join(['profile'+str(i)+'.stl' for i in range(len(rotations))])+' > mep.stl')

###Generating box
nPointFFD=20
os.system('xfoil << EOF\n naca9303\n gdes \n tgap 0.005\n0.3\n \nppar\nn '+str(2*nPointFFD)+'\nt 1\n \n \n psav box \n quit \n EOF')
box=numpy.loadtxt('box')
box[int(len(box)/2)-1]=[0,0.005]
box[int(len(box)/2)]=[0,-0.005]
boxWire0=Part.makePolygon([Base.Vector(*x) for x in box])

##translating scaling and rotating box
boxWireFlap=[boxWire0.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), rotations[ii]).scale(1).translate(Base.Vector(*translations[ii])) for ii in range(len(rotations))]
####### SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
for ii in range(len(boxWireFlap)):
    boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireFlap[ii].Vertexes])
    boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
    boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWireFlap[ii].Vertexes])
    boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
    numpy.savetxt('FFD/profile'+str(ii)+'.xyz',numpy.hstack([boxCoords,boxCoords2]))

os.system('cat '+(" ").join(['FFD/profile'+str(i)+'.xyz' for i in range(len(rotations))])+' > FFD/wing.xyz')
os.system("sed -i '1i"+str(len(rotations))+"\\n"+(" ").join([str(nPointFFD)+" 2 2" for ii in range(len(rotations))])+"' FFD/wing.xyz")

os.system("docker run -it --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '/home/dafoamuser/dafoam/packages/miniconda3/bin/dafoam_plot3d2tecplot.py FFD/wing.xyz deformedFFD.dat'")

exit()
