import random
import numpy as np
from time import time
from square import Square
from vector2 import Vec2d
from polygon import Polygon

def get_collision_depth(poly1, poly2, n):
	between_vec = poly1.mid - poly2.mid
	between = between_vec.dot(n)
	if between_vec.dot(n) < 0:
		between *= -1
		left_poly = poly2
		right_poly = poly1
	else:
		left_poly = poly1
		right_poly = poly2

	max_l2n = min([vertex.dot(n) for vertex in left_poly.vertices[:-1]])
	min_l2n = max([vertex.dot(n) for vertex in right_poly.vertices[:-1]])

	return (between - min_l2n + max_l2n)*-1, left_poly, right_poly

def get_collision_vectors(left_poly, right_poly, collision_vector):
	# Obs: wrong!
	get_vertex_length = lambda vertex: vertex.dot(collision_vector)

	max_l2n = min([vertex.dot(collision_vector) for vertex in left_poly.vertices[:-1]])
	min_l2n = max([vertex.dot(collision_vector) for vertex in right_poly.vertices[:-1]])

	keep_left_vertex = lambda vertex: get_vertex_length(vertex) == max_l2n
	keep_right_vertex = lambda vertex: get_vertex_length(vertex) == min_l2n

	left_collision_vertices = list(filter(keep_left_vertex, left_poly.vertices[:-1]))
	right_collision_vertices = list(filter(keep_right_vertex, right_poly.vertices[:-1]))

	left_collision_vertex = sum(left_collision_vertices)/len(left_collision_vertices)
	right_collision_vertex = sum(right_collision_vertices)/len(right_collision_vertices)

	left_collision_vector = left_poly.mid - (right_poly.mid + right_collision_vertex)
	right_collision_vector = right_poly.mid - (left_poly.mid + left_collision_vertex)

	return left_collision_vector, right_collision_vector

def is_colliding(poly1, poly2):
	# get list og uniqe normals
	normals = poly1.normals + poly2.normals
	for n1 in poly1.normals:
		for n2 in poly2.normals:
			if abs(n1.cross(n2)) < 1e-10:
				normals.remove(n1)

	# collision vector points from right_poly to left_poly
	min_collision_depth = float("Infinity")
	collision_vector = None
	final_left_poly, final_right_poly = None, None
	for n in normals:
		collision_depth, left_poly, right_poly = get_collision_depth(poly1, poly2, n)
		if collision_depth < 0:
			return False, None, None, None, None, None, None
		elif collision_depth < min_collision_depth:
			min_collision_depth = collision_depth
			collision_vector = n.copy()
			final_left_poly, final_right_poly = left_poly, right_poly

	# left and right collision vectors point from mid to collision point of other polygon
	left_collision_vector, right_collision_vector = get_collision_vectors(final_left_poly, final_right_poly, collision_vector)

	return True, final_left_poly, final_right_poly, min_collision_depth, collision_vector, left_collision_vector, right_collision_vector


if __name__ == '__main__':
	px2m = 50

	class Size(object):
		def __init__(self, w, h):
			self.w = w
			self.h = h
	screen_size = Size(720, 480)

	class Context():
		px2m = px2m
		px2m_func = lambda self, n: n*px2m
		px2m_tuple = lambda self, x, y: (x*px2m, y*px2m)
		screen_size_px = screen_size
		screen_size_m = Size(screen_size_px.w/px2m, screen_size_px.h/px2m)
	context = Context()

	poly1 = Square(context, 1, 1, 1, 1, 0, 1)
	poly2 = Square(context, 1.95, 0.7, 1, 1, 0, 1)

	# def cooly_pooly(mid, size, quality):
	# 	vertices = []
	# 	for theta in np.linspace(0, 2*np.pi, quality+1):
	# 		vertices.append(mid + Vec2d(np.cos(theta), np.sin(theta))*size)
	# 	return vertices
	#
	# poly2 = Polygon(context, cooly_pooly(Vec2d(2, 2), 1, 5))

	# loops = 10000
	#
	# start = time()
	# for i in range(loops):
	# 	poly1 = Square(context, 1, 1, 1, 1, random.random()*np.pi*2)
	# 	poly2 = Polygon(context, cooly_pooly(Vec2d(3, 2), 1, random.randint(3, 10)))
	# generate_time = time() - start
	#
	# start = time()
	# for i in range(loops):
	# 	poly1 = Square(context, 1, 1, 1, 1, random.random()*np.pi*2)
	# 	poly2 = Polygon(context, cooly_pooly(Vec2d(3, 2), 1, random.randint(3, 10)))
	#
	# 	colliding, left_poly, right_poly, collision_depth, collision_vector = is_colliding(poly1, poly2)
	#
	# collision_time = (time() - start) - generate_time
	# print(f"collision time: {collision_time/loops:.3g} s")

	colliding, *collision_data = is_colliding(poly1, poly2)
	left_poly, right_poly, collision_depth, collision_vector, left_collision_vector, right_collision_vector = collision_data
	print(left_poly.mid, right_poly.mid)
	print(left_collision_vector, right_collision_vector)

	spring_force = collision_vector*2000*collision_depth**(2/3)
	print(spring_force)
	print(left_collision_vector.cross(spring_force), right_collision_vector.cross(spring_force))
