
import FreeCAD,Mesh,Part,numpy
from FreeCAD import Base

doc=App.newDocument()

from freecad import module_io


for ii in range(1):
	module_io.OpenInsertObject("Mesh", "profile"+str(ii)+".stl", "insert")
	doc.addObject('Part::Feature', 'profile0'+str(ii))
	__shape__ = Part.Shape()
	__shape__.makeShapeFromMesh(doc.getObject('profile'+str(ii)).Mesh.Topology, 0.1, False)
	doc.getObject('profile0'+str(ii)).Shape = __shape__
	doc.getObject('profile0'+str(ii)).purgeTouched()
	del __shape__
	aa=doc.getObject("profile0"+str(ii)).Shape.Edges
	bb=[x for x in aa if x.CenterOfGravity.z<0.001]
	cc=Part.Wire(bb)
	Part.show(cc,"profile00"+str(ii))
	offset=cc.makeOffset2D(0.01)
	Part.show(offset,"offset00"+str(ii))
	boxCoords=numpy.array([[x.X,x.Y,x.Z] for x in offset.Vertexes[::10]])
	boxCoords=numpy.vstack((boxCoords[:int(len(boxCoords)/2)],boxCoords[:int(len(boxCoords)/2)-1:-1])).T
	boxCoords2=numpy.array([[x.X,x.Y,.1] for x in offset.Vertexes])
	boxCoords2=numpy.vstack((boxCoords2[:int(len(boxCoords2)/2)],boxCoords2[:int(len(boxCoords2)/2)-1:-1])).T
	numpy.savetxt('FFD/profile'+str(ii)+'.xyz',numpy.hstack([boxCoords,boxCoords2]))



os.system('cat '+(" ").join(['FFD/profile'+str(i)+'.xyz' for i in range(1)])+' > FFD/wing.xyz')
os.system("sed -i '1i"+str(len(range(1)))+"\\n"+(" ").join([str(len(offset.Vertexes[::10]))+" 2 2" for ii in range(len(range(1)))])+"' FFD/wing.xyz")

os.system("docker run -it --rm -u dafoamuser --mount \"type=bind,src=$(pwd),target=/home/dafoamuser/mount\" -w /home/dafoamuser/mount dafoam/opt-packages:v3.1.2 bash -c '/home/dafoamuser/dafoam/packages/miniconda3/bin/dafoam_plot3d2tecplot.py FFD/wing.xyz deformedFFD.dat'")
