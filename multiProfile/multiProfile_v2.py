import Part, FreeCAD, math, Draft,os,numpy,copy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')

if os.path.exists('box'):os.remove('box')

rotations=[0,-35]
translations=[[0,0],[1.02,-.08]]
#rotations=[0,-15,-30]
#translations=[[0,0],[1,-.1],[1.95,-.5]]
#rotations=[5,-10,-20,-30]
#translations=[[0,0],[1,-.15],[1.95,-.5],[2.95,-1]]

##wing sail
#rotations=[0,-15]
#translations=[[0,0],[1.02,-.08]]

if os.path.exists('profile0'):os.remove('profile0')

os.system('python spline.py')
profile0=numpy.loadtxt('profile0')

if os.path.exists('profile1'):os.remove('profile1')
os.system('xfoil << EOF\n naca9401\n gdes \ntset\n\n0.15\n tgap 0.005\n0.3\nlera 5 0.1\n\npcop\n psav profile1 \n quit \n EOF')#before tgap 0.015
profile1=numpy.loadtxt('profile1')

profiles=[list(profile0),list(profile1)]

profileWires=[Part.makePolygon([Base.Vector(*x) for x in profile+[profile[0]]]) for profile in profiles]

profileWire=[profileWires[ii].copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), rotations[ii]).scale(1).translate(Base.Vector(*translations[ii])) for ii in range(len(rotations))]
profileExtrude=[xx.extrude(Base.Vector(0,0,.1)) for xx in profileWire]
[profileExtrude[ii].exportStl('profile'+str(ii)+'.stl') for ii in range(len(rotations))]
[os.system('sed -i -e \'s#solid#solid profile'+str(ii)+'#g\' profile'+str(ii)+'.stl') for ii in range(len(rotations))]

os.system('cat '+(' ').join(['profile'+str(i)+'.stl' for i in range(len(rotations))])+' > mep.stl')

exit()
