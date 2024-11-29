import Part, FreeCAD, math, Draft,os,numpy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')
#NACA65004
os.system('xfoil << EOF\n naca9404\n gdes \n tgap 0.005\n0.3\n \npcop\n psav profile \n quit \n EOF')#before tgap 0.015
profile=numpy.loadtxt('profile')


os.system('xfoil << EOF\n naca9406\n gdes \n tgap 0.01\n0.3\n \nppar\nn 10\n \n \n psav box \n quit \n EOF')
box=numpy.loadtxt('box')
boxWire=Part.makePolygon([Base.Vector(*x) for x in box])

#boxWire.scale(1.05,Base.Vector(0.5,0,0))
#Part.show(boxWire,'boxWire')

boxWireScaled=boxWire.makeOffset2D(.03,join=2).Wires[0]
Part.show(boxWireScaled,'mainWire')
####### SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireScaled.Vertexes[1:]])
boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
boxCoords2=numpy.array([[x.X,x.Y,1] for x in boxWireScaled.Vertexes[1:]])
boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
numpy.savetxt('FFD/main.xyz',numpy.hstack([boxCoords,boxCoords2]))
#os.system("sed -i '1i1\\n5 2 2' FFD/main.xyz")

profileWire=Part.makePolygon([Base.Vector(*x) for x in profile])
Part.show(profileWire,'profileWire')

LE=profileWire.Vertexes[int(len(profileWire.Vertexes)/2)]
LE=numpy.array([LE.X,LE.Y,LE.Z])
TE1=profileWire.Vertexes[0]
TE2=profileWire.Vertexes[-1]
TE=(numpy.array([TE1.X,TE1.Y,TE1.Z])+numpy.array([TE2.X,TE2.Y,TE2.Z]))/2
LEcons=LE*0.98+TE*0.02
TEcons=LE*0.02+TE*0.98
numpy.savetxt('LEconsMain',LEcons)
numpy.savetxt('TEconsMain',TEcons)
Part.show(Part.Vertex(*LEcons))
Part.show(Part.Vertex(*TEcons))

profileExtrude=profileWire.extrude(Base.Vector(0,0,1))
Part.show(profileExtrude,'profileExtrude')

slatWire=profileWire.copy().rotate(Base.Vector(1,0,0),Base.Vector(0,0,1),30).scale(0.5).translate(Base.Vector(-0.53,0.01,0))
boxWireScaledSlat=boxWireScaled.copy().rotate(Base.Vector(1,0,0),Base.Vector(0,0,1),30).scale(0.5).translate(Base.Vector(-0.53,0.01,0))
Part.show(boxWireScaledSlat,'slatWire')

LE=slatWire.Vertexes[int(len(slatWire.Vertexes)/2)]
LE=numpy.array([LE.X,LE.Y,LE.Z])
TE1=slatWire.Vertexes[0]
TE2=slatWire.Vertexes[-1]
TE=(numpy.array([TE1.X,TE1.Y,TE1.Z])+numpy.array([TE2.X,TE2.Y,TE2.Z]))/2
LEcons=LE*0.95+TE*0.05
TEcons=LE*0.05+TE*0.95
numpy.savetxt('LEconsSlat',LEcons)
numpy.savetxt('TEconsSlat',TEcons)
####### SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireScaledSlat.Vertexes[1:]])
boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
boxCoords2=numpy.array([[x.X,x.Y,1] for x in boxWireScaledSlat.Vertexes[1:]])
boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
numpy.savetxt('FFD/slat.xyz',numpy.hstack([boxCoords,boxCoords2]))
#os.system("sed -i '1i1\\n5 2 2' FFD/slat.xyz")

flapWire=profileWire.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),-25).scale(0.5).translate(Base.Vector(1.01,-0.03,0))
Part.show(flapWire,'flapWire')
boxWireScaledFlap=boxWireScaled.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),-25).scale(0.5).translate(Base.Vector(1.01,-0.03,0))
Part.show(boxWireScaledFlap,'flapWire')

LE=flapWire.Vertexes[int(len(flapWire.Vertexes)/2)]
LE=numpy.array([LE.X,LE.Y,LE.Z])
TE1=flapWire.Vertexes[0]
TE2=flapWire.Vertexes[-1]
TE=(numpy.array([TE1.X,TE1.Y,TE1.Z])+numpy.array([TE2.X,TE2.Y,TE2.Z]))/2
LEcons=LE*0.98+TE*0.02
TEcons=LE*0.02+TE*0.98
numpy.savetxt('LEconsFlap',LEcons)
numpy.savetxt('TEconsFlap',TEcons)
Part.show(Part.Vertex(*LEcons))
Part.show(Part.Vertex(*TEcons))
####### SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireScaledFlap.Vertexes[1:]])
boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
boxCoords2=numpy.array([[x.X,x.Y,1] for x in boxWireScaledFlap.Vertexes[1:]])
boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
numpy.savetxt('FFD/flap.xyz',numpy.hstack([boxCoords,boxCoords2]))

os.system('cat FFD/main.xyz FFD/slat.xyz FFD/flap.xyz > FFD/wing.xyz')
os.system("sed -i '1i3\\n5 2 2 5 2 2 5 2 2' FFD/wing.xyz")

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

os.system('cartesian2DMesh')

os.system('renumberMesh -overwrite')

os.system('checkMesh')

os.system('cp -r 0.orig 0')

exit()
