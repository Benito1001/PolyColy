from polygon import Polygon
from vector2 import Vec2d

class Square(Polygon):
	def __init__(self, context, x, y, w, h, rot=0, color=(0, 0, 0), density=1):
		Polygon.__init__(self, context, self.get_vertex_points(x, y, w, h), density, color)
		self.set_rot(rot)

	def get_vertex_points(self, x, y, w, h):
		vertex_points = [
			Vec2d(x, y),
			Vec2d(x + w, y),
			Vec2d(x + w, y + h),
			Vec2d(x, y + h),
			Vec2d(x, y)
		]
		return vertex_points

class Player(Square):
	def __init__(self, context, x, y, w, h, rot, density):
		Square.__init__(self, context, x, y, w, h, rot, density)
		self.set_color((0, 150, 100))
		self.keys = {}

	def update(self, dt):
		power = 2
		if self.keys.get("w"):
			self.force.y -= power
		if self.keys.get("s"):
			self.force.y += power
		if self.keys.get("a"):
			self.force.x -= power
		if self.keys.get("d"):
			self.force.x += power

		self.force += -self.vel*0.5

		# if not self.immovable:
		self.acc = self.force/self.mass
		self.vel += self.acc*dt
		self.set_mid(self.mid + self.vel*dt)
		self.hitbox.set_pos(self.mid)
		self.force = Vec2d(0, 0)

		# if not self.imrotatable:
		self.rot_acc = self.tourqe/self.moofin
		self.rot_vel += self.rot_acc*dt
		self.set_rot(self.rot + self.rot_vel*dt)
		self.tourqe = 0
