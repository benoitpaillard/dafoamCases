import Part, FreeCAD, math, Draft,os,numpy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')

os.system('xfoil << EOF\n naca2412\n gdes \n tgap 0.005\n0.3\n \npcop\n psav profile \n quit \n EOF')#before tgap 0.015
profile=numpy.loadtxt('profile')

profileWire=Part.makePolygon([Base.Vector(*x) for x in profile])
Part.show(profileWire,'profileWire')

profileExtrude=profileWire.extrude(Base.Vector(0,0,1))
Part.show(profileExtrude,'profileExtrude')

slatWire=profileWire.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),15).scale(0.5).translate(Base.Vector(-0.5,-0.1,0))
flapWire=profileWire.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),-15).scale(0.5).translate(Base.Vector(1.,-0.05,0))

Part.show(slatWire,'slatWire')
Part.show(flapWire,'flapWire')

slatExtrude=slatWire.extrude(Base.Vector(0,0,1))
flapExtrude=flapWire.extrude(Base.Vector(0,0,1))

Part.show(slatExtrude,'slatExtrude')
Part.show(flapExtrude,'flapExtrude')

profileExtrude.exportStl('profileExtrude.stl')
slatExtrude.exportStl('slatExtrude.stl')
flapExtrude.exportStl('flapExtrude.stl')

os.system('sed -i -e \'s#solid#solid main#g\' profileExtrude.stl')
os.system('sed -i -e \'s#solid#solid slat#g\' slatExtrude.stl')
os.system('sed -i -e \'s#solid#solid flap#g\' flapExtrude.stl')

os.system('cat profileExtrude.stl slatExtrude.stl flapExtrude.stl > mep.stl')

os.system('surfaceGenerateBoundingBox mep.stl box.stl 10 10 10 10 0 0')

os.system('head -n -32 box.stl > temp.stl && mv temp.stl box.stl')
#### REMOVE ZMin and ZMax FROM STL FILE

os.system('cartesian2DMesh')
os.system('checkMesh')

exit()
