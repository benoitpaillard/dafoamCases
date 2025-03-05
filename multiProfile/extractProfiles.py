App.newDocument()
import os
import Mesh,Part,Draft
from FreeCAD import Base

meshDTC=Mesh.Mesh("/home/jony/dafoamCases/multiProfile/DTC-scaled.stl")

shapeDTC = Part.Shape()
shapeDTC.makeShapeFromMesh(meshDTC.Topology, 0.1,False)

mesh1=Mesh.Mesh(u"/home/jony/dafoamCases/multiProfile/profile0.stl")

shape1 = Part.Shape()
shape1.makeShapeFromMesh(mesh1.Topology, 0.1,False)

shape1.translate(Base.Vector(-0.5,0,0))

edges1=[x for x in shape1.Edges if x.CenterOfGravity.z<0.01]

wire1=Part.Wire(Part.sortEdges(edges1)[0])

Part.show(wire1,'wire1')

face1=Part.makeFace([wire1],'Part::FaceMakerSimple')
Part.show(face1)

wire1_top = Draft.make_clone(FreeCAD.ActiveDocument.getObject("wire1"))

wire1_top.Scale=Base.Vector(.4,.4,1)
wire1_top.Placement.Base=Base.Vector(0,0,3)
wire1_top.recompute()

sail1=Part.makeRuledSurface(wire1,wire1_top.Shape)

Part.show(sail1)

face1_top=Part.makeFace([wire1_top.Shape],'Part::FaceMakerSimple')
Part.show(face1_top)

mesh2=Mesh.Mesh(u"/home/jony/dafoamCases/multiProfile/profile1.stl")

shape2 = Part.Shape()
shape2.makeShapeFromMesh(mesh2.Topology, 0.1,False)

shape2.translate(Base.Vector(-0.5,0,0))

edges2=[x for x in shape2.Edges if x.CenterOfGravity.z<0.01]

### FURLER OPPOSITE SIDE
oppEdge=[x for x in edges2 if x.CenterOfGravity.x==min([x.CenterOfGravity.x for x in edges2])][0]
oppEdge_top=oppEdge.copy()
oppEdge_top.scale(.4,Base.Vector(0,0,0))
oppEdge_top.translate(Base.Vector(0,0,3))
oppPoint=oppEdge.CenterOfGravity
oppPoint.scale(-1,1,1)
oppPoint_top=oppEdge_top.CenterOfGravity
oppPoint_top.scale(-1,1,1)
delta=oppPoint_top.sub(oppPoint)
furler = Part.makeCylinder(0.01, delta.Length,oppPoint, delta)
Part.show(furler)



wire2=Part.Wire(Part.sortEdges(edges2)[0])

Part.show(wire2,'wire2')

face2=Part.makeFace([wire2],'Part::FaceMakerSimple')
Part.show(face2)

wire2_top=wire2.copy()
wire2_top.scale(.4,Base.Vector(0,0,0))
#Part.show(wire2_top,'wire2_top')

#wire2_top = Draft.make_clone(FreeCAD.ActiveDocument.getObject("wire2"))
#wire2_top.Scale=Base.Vector(.9,.9,1)

wire2_top.Placement.Base=Base.Vector(0,0,3)
#wire2_top.recompute()

sail2=Part.makeRuledSurface(wire2,wire2_top)

Part.show(sail2)

face2_top=Part.makeFace([wire2_top],'Part::FaceMakerSimple')
Part.show(face2_top)

sail=Part.makeCompound([sail1,sail2,face1,face1_top,face2,face2_top,furler])
sail.scale(.5)

Part.show(sail)

sail.exportStl('patch0.stl')
