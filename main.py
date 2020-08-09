import time
import pygame
import random
import itertools
import numpy as np
from square import Square, Player
from vector2 import Vec2d
from polygon import Polygon
from collision import is_colliding

pygame.init()

clock = pygame.time.Clock()
mainloop = True
fps = 60
playtime = 0.0

px2m = 75


class Size(object):
	def __init__(self, w, h):
		self.w = w
		self.h = h
screen_size = Size(int(1920/1.5), int(1080/1.5))
screen = pygame.display.set_mode((screen_size.w, screen_size.h))

background = pygame.Surface(screen.get_size())
background.fill((255, 255, 255))
background = background.convert()
screen.blit(background, (0, 0))

entities = []

class Context():
	px2m = px2m
	px2m_func = lambda self, n: n*px2m
	px2m_tuple = lambda self, x, y: (x*px2m, y*px2m)
	screen_size_px = screen_size
	screen_size_m = Size(screen_size_px.w/px2m, screen_size_px.h/px2m)
	screen = screen
	background = background
	entities = entities
context = Context()


player = Player(context, 1, 1, 1, 1, 0, 1)

entities.append(player)

def cooly_pooly(mid, size, quality):
	vertices = []
	# for theta in np.linspace(0, 2*np.pi, quality+1):
	# 	vertices.append(mid + Vec2d(float(np.cos(theta)), float(np.sin(theta)))*size)
	prev_theta = 0
	for n in range(quality + 1):
		vertices.append(mid + Vec2d(float(np.cos(prev_theta)), float(np.sin(prev_theta)))*size)
		theta = prev_theta + random.random()*(2*np.pi - prev_theta)/2
		prev_theta = theta
	return vertices[:-1]

# entities.append(Square(context, 3, 2, 3, 1, 3.14/4, 1))
for x in range(3, 16, 4):
	for y in range(2, 9, 3):
			entities.append(Polygon(context, cooly_pooly(Vec2d(x, y), 1, random.randint(3, 9)), 1))

# entities.append(Polygon(context, [
# 	Vec2d(4, 4), Vec2d(5, 5), Vec2d(4, 6), Vec2d(3.3, 5.9), Vec2d(3, 5)
# ]))
# poly1_pos = Vec2d(0.5, 4.25)
# poly1 = Polygon(context, [
# 	poly1_pos, poly1_pos+(1, 0), poly1_pos+(1, 1), poly1_pos+(0, 1)
# ])
# entities.append(poly1)
# #
# poly1_pos = Vec2d(2, 2)
# poly2 = Polygon(context, [
# 	poly1_pos, poly1_pos+(1, 1), poly1_pos+(0, 2), poly1_pos+(-0.7, 1.9), poly1_pos+(-1, 1)
# ])
# entities.append(poly2)

end_time, start_time, dt = 1, 1, 1
time_saturations = []

# saturation_data = open("satdat.txt", "w")

while mainloop:
	# Print framerate and playtime in titlebar
	milliseconds = clock.tick(fps)
	true_fps = clock.get_fps()
	playtime += milliseconds/1000

	time_saturation = 100*(end_time - start_time)/dt
	time_saturations.append(time_saturation)
	if len(time_saturations) > 60:
		time_saturations.pop(0)
	# saturation_data.write(f"{playtime} {time_saturation}\n")

	text = f"fps: {true_fps:.2f}   Frame saturation: {sum(time_saturations)/len(time_saturations):.0f} %"
	pygame.display.set_caption(text)
	if true_fps != 0:
		dt = 1/true_fps
	else:
		dt = 1/fps

	start_time = time.time()

	# Event handeler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			mainloop = False
		elif event.type == pygame.KEYDOWN:
			key_name = pygame.key.name(event.key)
			player.keys[key_name] = True
			if event.key == pygame.K_ESCAPE:
				mainloop = False
		elif event.type == pygame.KEYUP:
			key_name = pygame.key.name(event.key)
			player.keys[key_name] = False

	# player.set_rot(player.rot + 0.1)
	# Update and Draw
	quality = 10
	for i in range(quality):
		for ent1, ent2 in itertools.combinations(entities, 2):
			if ent1.hitbox.collides(ent2.hitbox):
				colliding, *collision_data = is_colliding(ent1, ent2)
				if colliding:
					left_poly, right_poly, collision_depth, collision_vector, left_collision_vector, right_collision_vector = collision_data

					spring_force = collision_vector*1000*collision_depth**(2/3)
					left_poly.force += spring_force
					right_poly.force -= spring_force

					left_poly.tourqe += left_collision_vector.cross(spring_force)
					right_poly.tourqe += right_collision_vector.cross(-spring_force)

		for entity in entities:
			entity.update(dt/quality)

	screen.blit(background, (0, 0))
	for entity in entities:
		entity.draw()

	# Update Pygame display.
	pygame.display.flip()

	end_time = time.time()

# Finish Pygame.
pygame.quit()
# saturation_data.close()
