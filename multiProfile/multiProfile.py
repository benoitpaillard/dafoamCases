import Part, FreeCAD, math, Draft,os,numpy,copy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')

if os.path.exists('box'):os.remove('box')

#rotations=[0,-35]
rotations=[0,-20]
#translations=[[0,0],[1.02,-.08]]
translations=[[0,0],[1.02-0.5,-.08]]
scales=[0.8,1.2]
#rotations=[0,-15,-30]
#translations=[[0,0],[1,-.1],[1.95,-.5]]
#rotations=[5,-10,-20,-30]
#translations=[[0,0],[1,-.15],[1.95,-.5],[2.95,-1]]

##wing sail
#rotations=[0,-15]
#translations=[[0,0],[1.02,-.08]]

### Generating circle
#circleIntra=0.5*numpy.array([[numpy.cos(t)+1,numpy.sin(t)] for t in numpy.linspace(0,0.7*numpy.pi,100)])
#circleExtra=0.5*numpy.array([[numpy.cos(t)*1.01+1,numpy.sin(t)*1.01] for t in numpy.linspace(0,0.7*numpy.pi,100)])
#circle=numpy.vstack((circleExtra,circleIntra[::-1]))
#numpy.savetxt('circle.dat',circle)
##from pylab import *
##plot(*circle.T)
##show()

##Generating profile
if os.path.exists('profile0'):os.remove('profile0')

#os.system('xfoil << EOF\n naca9509\n gdes \ntset\n\n0.3\n tgap 0.005\n0.3\nlera 5 0.1\n\npcop\n psav profile0 \n quit \n EOF')#before tgap 0.015
os.system('xfoil << EOF\n naca9509\n gdes \n tgap 0.005\n0.3\n\npcop\n psav profile0 \n quit \n EOF')#before tgap 0.015
#os.system('xfoil << EOF\n load circle.dat\n\ngdes\ndero\nunit\n\npcop\n psav profile0 \n quit \n EOF')#before tgap 0.015

##wing sail
#os.system('xfoil << EOF\n naca0015\n gdes \n tgap 0.005\n0.3\n\npcop\n psav profile0 \n quit \n EOF')#before tgap 0.015

profile0=numpy.loadtxt('profile0')
## build symmetrical profile
profile0=profile0[profile0[:,0]<0.5]
profile0[:,0]-=0.5
profile0_2=copy.deepcopy(profile0)
profile0_2[:,0]*=-1
profile0=numpy.vstack([profile0,profile0_2[::-1]])
profile0[:,0]+=0.5
profile0=numpy.roll(profile0,int(len(profile0)*0.25),axis=0)
#from pylab import *
#plot(*profile0.T)
#show()

if os.path.exists('profile1'):os.remove('profile1')

os.system('xfoil << EOF\n naca9401\n gdes \ntset\n\n0.15\n tgap 0.005\n0.3\nlera 5 0.1\n\npcop\n psav profile1 \n quit \n EOF')#before tgap 0.015

##wing sail
#os.system('xfoil << EOF\n naca0015\n gdes \n tgap 0.005\n0.3\n\npcop\n psav profile1 \n quit \n EOF')#before tgap 0.015


#profile=list(numpy.loadtxt('profile'))

profiles=[list(profile0),list(numpy.loadtxt('profile1'))]

profileWires=[Part.makePolygon([Base.Vector(*x) for x in profile+[profile[0]]]) for profile in profiles]

profileWire=[profileWires[ii].copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), rotations[ii]).scale(scales[ii]).translate(Base.Vector(*translations[ii])) for ii in range(len(rotations))]
profileExtrude=[xx.extrude(Base.Vector(0,0,.1)) for xx in profileWire]
[profileExtrude[ii].exportStl('profile'+str(ii)+'.stl') for ii in range(len(rotations))]
[os.system('sed -i -e \'s#solid#solid profile'+str(ii)+'#g\' profile'+str(ii)+'.stl') for ii in range(len(rotations))]

os.system('cat '+(' ').join(['profile'+str(i)+'.stl' for i in range(len(rotations))])+' > mep.stl')

###Generating box
nPointFFD=10

#circleIntra=0.5*numpy.array([[numpy.cos(t)+1,numpy.sin(t)] for t in numpy.linspace(0,0.7*numpy.pi,100)])
#circleExtra=0.5*numpy.array([[numpy.cos(t)*1.01+1,numpy.sin(t)*1.01] for t in numpy.linspace(0,0.7*numpy.pi,100)])
#circle=numpy.vstack((circleExtra,circleIntra[::-1]))
#numpy.savetxt('circle.dat',circle)

if os.path.exists('box0'):os.remove('box0')

#os.system('xfoil << EOF\n load circle.dat\n\ngdes\ndero\nunit\n\nppar\nn '+str(2*nPointFFD)+'\nt 1\np 0.1\n \n \n psav box0 \n quit \n EOF')
#os.system('xfoil << EOF\n naca9512\n gdes \ntset\n\n0.3\n tgap 0.015\n0.3\nlera 5 0.1\n\nppar\nn '+str(2*nPointFFD)+'\nt 0.5\np 1\n \n \n psav box0 \n quit \n EOF')
os.system('xfoil << EOF\n naca9512\n gdes \n tgap 0.015\n0.3\n\nppar\nn '+str(2*nPointFFD)+'\nt 1\np 0.1\n \n \n psav box0 \n quit \n EOF')

##wing sail
#os.system('xfoil << EOF\n naca0015\n gdes \n tgap 0.015\n0.3\n\nppar\nn '+str(2*nPointFFD)+'\nt 0.5\np 1\n \n \n psav box0 \n quit \n EOF')

box0=numpy.loadtxt('box0')
## build symmetrical box
box0[int(len(box0)/2)-1]=[-.01,0.02]
box0[int(len(box0)/2)]=[-.01,-0.02]
box0=box0[int(nPointFFD*0.5):int(nPointFFD*1.5)]
box0[:,0]-=0.5
box0_2=copy.deepcopy(box0)
box0_2[:,0]*=-1
box0=numpy.vstack([box0,box0_2[::-1]])
box0[:,0]+=0.5
box0=numpy.roll(box0,int(nPointFFD*0.5),axis=0)
#from pylab import *
#plot(*box0.T)
#show()

if os.path.exists('box1'):os.remove('box1')

os.system('xfoil << EOF\n naca9403\n gdes \ntset\n\n0.15\n tgap 0.015\n0.3\nlera 5 0.1\n\nppar\nn '+str(2*nPointFFD)+'\nt 1\np 0.1\n \n \n psav box1 \n quit \n EOF')
#os.system('xfoil << EOF\n load profilCl2\n gdes \ntset\n0.05\n\n tgap 0.015\n1\n \nppar\nn '+str(2*nPointFFD)+'\nt 1\np 0.1\n \n \n psav box \n quit \n EOF')

##wing sail
#os.system('xfoil << EOF\n naca0015\n gdes \n tgap 0.015\n0.3\n\nppar\nn '+str(2*nPointFFD)+'\nt 0.5\np 1\n \n \n psav box1 \n quit \n EOF')

boxes=[box0,numpy.loadtxt('box1')]

## for cirles
#boxes[0][int(len(boxes[0])/2)-1]=[-0.01,-0.005]
#boxes[0][int(len(boxes[0])/2)]=[0.01,-0.01]

## for airfoils
#boxes[0][int(len(boxes[0])/2)-1]=[-.01,0.02]
#boxes[0][int(len(boxes[0])/2)]=[-.01,-0.02]
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

os.system("docker run -it --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '/home/dafoamuser/dafoam/packages/miniconda3/bin/dafoam_plot3d2tecplot.py FFD/wing.xyz deformedFFD.dat'")

exit()
