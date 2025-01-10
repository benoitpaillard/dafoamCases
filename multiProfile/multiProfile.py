import Part, FreeCAD, math, Draft,os,numpy
from FreeCAD import Base

doc=FreeCAD.newDocument()

if os.path.exists('profile'):os.remove('profile')
#NACA65004
os.system('xfoil << EOF\n naca9301\n gdes \n tgap 0.001\n0.3\n \npcop\n psav profile \n quit \n EOF')#before tgap 0.015
profile=list(numpy.loadtxt('profile'))

profileWire=Part.makePolygon([Base.Vector(*x) for x in profile+[profile[0]]])
Part.show(profileWire,'profileWire')

nPointFFD=20

os.system('xfoil << EOF\n naca9303\n gdes \n tgap 0.005\n0.3\n \nppar\nn '+str(2*nPointFFD)+'\nt 1\n \n \n psav box \n quit \n EOF')
box=numpy.loadtxt('box')

box[int(len(box)/2)-1]=[0,0.005]
box[int(len(box)/2)]=[0,-0.005]

boxWire=Part.makePolygon([Base.Vector(*x) for x in box])

#boxWire.scale(1.05,Base.Vector(0.5,0,0))
Part.show(boxWire,'boxWire')
##WITHOUT OFFSET 2D
boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWire.Vertexes])
boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWire.Vertexes])
boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
numpy.savetxt('FFD/main.xyz',numpy.hstack([boxCoords,boxCoords2]))

#boxWire=boxWire.makeOffset2D(.02,join=2).Wires[0]
#Part.show(boxWire,'mainWire')
######## SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
##WITH OFFSET 2D
#boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWire.Vertexes[1:]])
#boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
#boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWire.Vertexes[1:]])
#boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
#numpy.savetxt('FFD/main.xyz',numpy.hstack([boxCoords,boxCoords2]))
##os.system("sed -i '1i1\\n5 2 2' FFD/main.xyz")

#LE=profileWire.Vertexes[int(len(profileWire.Vertexes)/2)]
#LE=numpy.array([LE.X,LE.Y,LE.Z])
#TE1=profileWire.Vertexes[0]
#TE2=profileWire.Vertexes[-1]
#TE=(numpy.array([TE1.X,TE1.Y,TE1.Z])+numpy.array([TE2.X,TE2.Y,TE2.Z]))/2
#LEcons=[0.005,0.0025,0]#LE*0.98+TE*0.02
#TEcons=[0.995,0.001,0]#LE*0.02+TE*0.98
#numpy.savetxt('LEconsMain',LEcons)
#numpy.savetxt('TEconsMain',TEcons)
#Part.show(Part.Vertex(*LEcons))
#Part.show(Part.Vertex(*TEcons))

profileExtrude=profileWire.extrude(Base.Vector(0,0,.1))
Part.show(profileExtrude,'profileExtrude')

#slatWire=profileWire.copy().rotate(Base.Vector(1,0,0),Base.Vector(0,0,1),30).scale(0.2).translate(Base.Vector(-0.2,0.02,0))
#boxWireSlat=boxWire.copy().rotate(Base.Vector(1,0,0),Base.Vector(0,0,1),30).scale(0.2).translate(Base.Vector(-0.2,0.02,0))
#Part.show(boxWireSlat,'slatWire')

#LESlat=slatWire.Vertexes[int(len(slatWire.Vertexes)/2)]
#LESlat=numpy.array([LESlat.X,LESlat.Y,LESlat.Z])
#TE1Slat=slatWire.Vertexes[0]
#TE2Slat=slatWire.Vertexes[-1]
#TESlat=(numpy.array([TE1Slat.X,TE1Slat.Y,TE1Slat.Z])+numpy.array([TE2Slat.X,TE2Slat.Y,TE2Slat.Z]))/2
#LEconsSlat=LESlat*0.95+TESlat*0.05
#TEconsSlat=LESlat*0.05+TESlat*0.95
#numpy.savetxt('LEconsSlat',LEconsSlat)
#numpy.savetxt('TEconsSlat',TEconsSlat)
######## SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
#boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireSlat.Vertexes[1:]])
#boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
#boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWireSlat.Vertexes[1:]])
#boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
#numpy.savetxt('FFD/slat.xyz',numpy.hstack([boxCoords,boxCoords2]))
##os.system("sed -i '1i1\\n5 2 2' FFD/slat.xyz")
#Part.show(slatWire,'slatWire')
#slatExtrude=slatWire.extrude(Base.Vector(0,0,1))
#Part.show(slatExtrude,'slatExtrude')
#slatExtrude.exportStl('slatExtrude.stl')

angleFlap=-30

flapWire=profileWire.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1), angleFlap).scale(1).translate(Base.Vector(1.0,-0.05,0))
Part.show(flapWire,'flapWire')
boxWireFlap=boxWire.copy().rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),angleFlap).scale(1).translate(Base.Vector(1.0,-0.05,0))
Part.show(boxWireFlap,'flapWire')

#LEFlap=flapWire.Vertexes[int(len(flapWire.Vertexes)/2)]
#LEFlap=numpy.array([LEFlap.X,LEFlap.Y,LEFlap.Z])
#TE1Flap=flapWire.Vertexes[0]
#TE2Flap=flapWire.Vertexes[-1]
#TEFlap=(numpy.array([TE1Flap.X,TE1Flap.Y,TE1Flap.Z])+numpy.array([TE2Flap.X,TE2Flap.Y,TE2Flap.Z]))/2
#LEconsFlap=LEFlap*0.98+TEFlap*0.02#last term = camber * chord * distance to nose
#TEconsFlap=LEFlap*0.02+TEFlap*0.98
##TEconsFlap=[1.864,-0.548,0]
##TEconsFlap=[1.954,-0.3025,0]
#numpy.savetxt('LEconsFlap',LEconsFlap)
#numpy.savetxt('TEconsFlap',TEconsFlap)
#Part.show(Part.Vertex(*LEconsFlap))
#Part.show(Part.Vertex(*TEconsFlap))

####### SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
##WITHOUT OFFSET 2D
boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireFlap.Vertexes])
boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWireFlap.Vertexes])
boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
numpy.savetxt('FFD/flap.xyz',numpy.hstack([boxCoords,boxCoords2]))

######## SHITTY HACK TO REORDER POINTS FOR PLOT3D FORMAT
##WITH OFFSET 2D
#boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in boxWireFlap.Vertexes[1:]])
#boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
#boxCoords2=numpy.array([[x.X,x.Y,.1] for x in boxWireFlap.Vertexes[1:]])
#boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
#numpy.savetxt('FFD/flap.xyz',numpy.hstack([boxCoords,boxCoords2]))

#os.system('cat FFD/main.xyz FFD/slat.xyz FFD/flap.xyz > FFD/wing.xyz')
#os.system("sed -i '1i3\\n5 2 2 5 2 2 5 2 2' FFD/wing.xyz")
os.system('cat FFD/main.xyz FFD/flap.xyz > FFD/wing.xyz')
os.system("sed -i '1i2\\n"+str(nPointFFD)+" 2 2 "+str(nPointFFD)+" 2 2' FFD/wing.xyz")

os.system("docker run -it --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '/home/dafoamuser/dafoam/packages/miniconda3/bin/dafoam_plot3d2tecplot.py FFD/wing.xyz deformedFFD.dat'")

Part.show(flapWire,'flapWire')

flapExtrude=flapWire.extrude(Base.Vector(0,0,.1))

Part.show(flapExtrude,'flapExtrude')

profileExtrude.exportStl('profileExtrude.stl')
flapExtrude.exportStl('flapExtrude.stl')

os.system('sed -i -e \'s#solid#solid main#g\' profileExtrude.stl')
#os.system('sed -i -e \'s#solid#solid slat#g\' slatExtrude.stl')
os.system('sed -i -e \'s#solid#solid flap#g\' flapExtrude.stl')

#os.system('cat profileExtrude.stl slatExtrude.stl flapExtrude.stl > mep.stl')
os.system('cat profileExtrude.stl flapExtrude.stl > mep.stl')

exit()
