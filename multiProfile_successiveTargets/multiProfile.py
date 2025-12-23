import Part, FreeCAD, math, Draft,os,numpy,copy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')
if os.path.exists('box'):os.remove('box')

rotations=[0,-38.01979412]#[0,-40]
translations=[[0,0],[0.9664187219-.2,-0.1465122362]]#[[0,0],[0.98,-.12]]
scales=[0.8,1.2]#[1,1]


##Generating profile
if os.path.exists('profile0'):os.remove('profile0')

### from splines
os.system('python spline.py')
profile0=numpy.loadtxt('profile0')

if os.path.exists('profile1'):os.remove('profile1')

os.system('xfoil << EOF\n naca9401\n gdes \ntset\n\n0.1406803934\n tgap 0.005\n0.3\nlera 5 0.1\n\npcop\n psav profile1 \n quit \n EOF')#before tgap 0.015

profiles=[list(profile0),list(numpy.loadtxt('profile1'))]

profileWires=[Part.makePolygon([Base.Vector(*x) for x in profile+[profile[0]]]) for profile in profiles]

profileWire=[profileWires[ii].copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), rotations[ii]).scale(scales[ii]).translate(Base.Vector(*translations[ii])) for ii in range(len(rotations))]
profileExtrude=[xx.extrude(Base.Vector(0,0,.1)) for xx in profileWire]
[profileExtrude[ii].exportStl('profile'+str(ii)+'.stl') for ii in range(len(rotations))]
[os.system('sed -i -e \'s#solid#solid profile'+str(ii)+'#g\' profile'+str(ii)+'.stl') for ii in range(len(rotations))]

os.system('cat '+(' ').join(['profile'+str(i)+'.stl' for i in range(len(rotations))])+' > mep.stl')

###Generating box
### from splines
box0=numpy.loadtxt('box0')

nPointFFD=int(len(box0)/2)

if os.path.exists('box1'):os.remove('box1')

os.system('xfoil << EOF\n naca9403\n gdes \ntset\n\n0.1406803934\n tgap 0.015\n0.3\nlera 5 0.1\n\nppar\nn '+str(2*nPointFFD)+'\nt 1\np 0.1\n \n \n psav box1 \n quit \n EOF')

boxes=[box0,numpy.loadtxt('box1')]

## for airfoils
boxes[1][int(len(boxes[1])/2)-1]=[0,0.005]
boxes[1][int(len(boxes[1])/2)]=[0,-0.005]

boxWires=[Part.makePolygon([Base.Vector(*x) for x in box]) for box in boxes]

##translating scaling and rotating box
boxWireFlap=[boxWires[ii].copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), rotations[ii]).scale(scales[ii]).translate(Base.Vector(*translations[ii])) for ii in range(len(rotations))]
####### SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
for ii in range(len(boxWireFlap)):
    boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireFlap[ii].Vertexes])
    boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
    boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWireFlap[ii].Vertexes])
    boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
    numpy.savetxt('FFD/profile'+str(ii)+'.xyz',numpy.hstack([boxCoords,boxCoords2]))

os.system('cat '+(" ").join(['FFD/profile'+str(i)+'.xyz' for i in range(len(rotations))])+' > FFD/wing.xyz')
os.system("sed -i '1i"+str(len(rotations))+"\\n"+(" ").join([str(nPointFFD)+" 2 2" for ii in range(len(rotations))])+"' FFD/wing.xyz")

os.system("docker run --rm -u dafoamuser --cpus='1' --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '/home/dafoamuser/dafoam/packages/miniconda3/bin/dafoam_plot3d2tecplot.py FFD/wing.xyz deformedFFD.dat'")

exit()
