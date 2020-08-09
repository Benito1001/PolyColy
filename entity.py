from vector2 import Vec2d

class Entity:
	def __init__(self, context):
		self.context = context
		self.px2m = self.context.px2m_func
		self.px2m_tuple = self.context.px2m_tuple
		self.screen_w = self.context.screen_size_m.w
		self.screen_h = self.context.screen_size_m.h

		self.vel = Vec2d(0, 0)
		self.acc = Vec2d(0, 0)
		self.force = Vec2d(0, 0)

		self.rot_vel = 0
		self.rot_acc = 0
		self.tourqe = 0

class Hitbox:
	def __init__(self, pos, w, h):
		self.pos = pos
		self.w = w
		self.h = h

	def set_pos(self, mid):
		self.pos = mid - (self.w/2, self.h/2)

	def collides(self, other):
		if (
			self.pos.x + self.w > other.pos.x and self.pos.x < other.pos.x + other.w
			and self.pos.y + self.h > other.pos.y and self.pos.y < other.pos.y + other.h
		):
			return True
		return False
