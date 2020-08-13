import pygame
from entity import Entity, Hitbox
from vector2 import Vec2d

class Polygon(Entity):
	def __init__(self, context, vertex_points, density=1, color=(0, 0, 0)):
		Entity.__init__(self, context)

		self.color = color
		self.rot = 0
		self.density = density

		self.update_vertex_points(vertex_points)
		self.update_surface()

	def update(self, dt):
		# if not self.immovable:
		# self.acc = self.force/self.mass
		# self.vel += self.acc*dt
		# self.set_mid(self.mid + self.vel*dt)
		# self.hitbox.set_pos(self.mid)
		# self.force = Vec2d(0, 0)

		# if not self.imrotatable:
		self.rot_acc = self.tourqe/self.moofin
		self.rot_vel += self.rot_acc*dt
		if self.rot_vel != 0:
			self.set_rot(self.rot + self.rot_vel*dt)
		self.tourqe = 0

	def draw(self):
		if self.surface_dirty:
			self.update_surface()
		self.context.screen.blit(self.Surface, self.px2m_tuple(*self.hitbox.pos))

	def update_vertex_points(self, vertex_points):
		self.vertex_points = vertex_points
		if self.vertex_points[0].x != self.vertex_points[-1].x or self.vertex_points[0].y != self.vertex_points[-1].y:
			self.vertex_points.append(Vec2d(self.vertex_points[0].x, self.vertex_points[0].y))

		self.area, self.mid = self.get_area_and_mid()
		self.vertices = [vertex_point - self.mid for vertex_point in self.vertex_points]
		self.mass = self.density*self.area
		self.moofin = self.get_moofin()
		self.edges = self.get_edges()
		self.normals = self.get_normals()
		self.hitbox = self.get_hitbox()

		self.surface_dirty = True

	def update_surface(self):
		self.Surface = pygame.Surface((self.px2m(self.hitbox.w), self.px2m(self.hitbox.h)))
		self.Surface.fill((255, 255, 255))
		self.Surface.set_colorkey((255, 255, 255))
		pix_vertices = [self.px2m_tuple(*(vertex_point - self.hitbox.pos)) for vertex_point in self.vertex_points]
		pygame.draw.polygon(self.Surface, self.color, pix_vertices)
		self.Surface = self.Surface.convert()

		self.surface_dirty = False

	def set_color(self, color):
		if color != self.color:
			self.color = color
			self.surface_dirty = True

	def get_area_and_mid(self):
		n = len(self.vertex_points) - 2
		P0 = self.vertex_points[0]

		total_area = 0
		midpoints = Vec2d(0, 0)
		for i in range(1, n):
			Pi, Pii = self.vertex_points[i], self.vertex_points[i+1]

			area = abs((Pi - P0).cross(Pii - P0))
			total_area += area
			midpoints += ((P0 + Pi + Pii)/3)*area

		return total_area/2, midpoints/total_area

	def set_mid(self, new_mid):
		self.mid = new_mid
		self.vertex_points = [vertex + self.mid for vertex in self.vertices]

	def get_moofin(self):
		moofin = 0
		total_area = 0
		for i in range(0, len(self.vertices) - 1):
			vi, vii = self.vertices[i], self.vertices[i+1]

			area = abs(vii.cross(vi))
			submoof = vi.get_length_sqrd() + vi.dot(vii) + vii.get_length_sqrd()

			moofin += area*submoof
			total_area += area

		return self.mass*(moofin/total_area)/6

	def set_rot(self, new_rot):
		dr = new_rot - self.rot
		new_vertex_points = [self.mid + vertex.rotate(-dr) for vertex in self.vertices]
		self.update_vertex_points(new_vertex_points)
		self.rot = new_rot

	def get_edges(self):
		edges = []
		for i in range(len(self.vertices) - 1):
			edges.append([self.vertices[i], self.vertices[i+1]])
		return edges

	def get_normals(self):
		normals = []
		for edge in self.edges:
			edge_vector = edge[1] - edge[0]
			new_normal = Vec2d(-edge_vector.y, edge_vector.x)/edge_vector.length
			for normal in normals:
				if abs(new_normal.cross(normal)) < 1e-10:
					break
			else:
				normals.append(new_normal)
		return normals

	def get_hitbox(self):
		top = self.vertex_points[0].y
		bottom = self.vertex_points[0].y
		left = self.vertex_points[0].x
		right = self.vertex_points[0].x
		for point in self.vertex_points[1:]:
			top = min(top, point.y)
			bottom = max(bottom, point.y)
			left = min(left, point.x)
			right = max(right, point.x)
		return Hitbox(Vec2d(left, top), right-left, bottom-top)
