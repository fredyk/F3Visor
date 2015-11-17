from _3dlib import *

class Polygon():

	code = -1
	face = None
	paint = None
	obj = None

	def __init__(self, face, code=-1, paint = None, obj = None):
		self.face = face
		self.code = code
		self.paint = paint
		self.obj = obj

	def getCode(self, args = None):
		return self.code

	def getFace(self):
		return self.face

	def getPaint(self):
		return self.paint

	def setCode(self, code):
		prev = self.code
		self.code = code
		return prev

	def setFace(self, face):
		self.face = face

	def setPaint(self, paint):
		self.paint = paint

	def getObj(self):
		return self.obj

class Volume():

	vertex = []
	faces  = []
	polygons = []
	rots   = []
	changed = True
	name = ""
	color = "blue"
	last_paint = 0

	def __init__(self, orivertex, faces, name, color="blue"):
		self.orivertex = orivertex
		self.vertex = orivertex[::]
		self.faces  = faces
		self.name = name
		self.color = color

	def addVert(self, vert):
		if(len(vert)==3):
			self.changed = True
			self.orivertex.append(vert)
			for angle in self.rots:
				vert = rot([vert], angle)[0]
			self.vertex.append(vert)
		else:
			print "error bad vert"

	def addFace(self, face):
		self.changed = True
		self.faces.append(face)
		self.polygons.append(Polygon(face, obj=self))

	def getVertex(self):
		return self.vertex

	def getScaledVerts(self, scale):
		return [ tuple( [ c*scale for c in v ] ) for v in self.vertex ]

	def getCords(self, visor, visor_rot, visor_disp, scale):
		# return c3dto2d(
		# 	mov(
  #           	rot(self.getScaledVerts(scale), [(visor, visor_rot)]),
  #           	[(visor_disp)]
  #           	),
  #           visor=visor, _int = True )
		return c3dto2d(
			rot(
            	mov(
            		self.getScaledVerts(scale), [(visor_disp)]
            		# self.getScaledVerts(scale), [(visor, visor_rot)]
            		),
            	[(
            		mov(
            			[visor],
            			[(visor_disp)]
            			)[0],
            		visor_rot)]
            	),
            visor=visor, _int = True )

	def getFaces(self):
		return self.faces

	def getPolygons(self, start = 0):
		# return self.polygons
		for i, pol in enumerate(self.polygons):
			if i < start: pass
			else:
				yield pol

	def rotate(self, angle): # angle includes center, i.e.:
							 # [ ( (0, 0, 0), (1, 1, 1) ), ...]
		init = now()
		self.changed = True
		self.rots.append(angle)
		self.vertex = rot(
            self.vertex,
            angle
            )
		return (now() - init) or 1e-6

	def noChanges(self):
		self.changed = False