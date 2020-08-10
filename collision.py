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
	# still wrong, somewhat close

	# get "x"-component of collision point
	x_vector = collision_vector
	depth_x, left_poly_x, right_poly_x = get_collision_depth(left_poly, right_poly, x_vector)
	rmin_x = max([vertex.dot(x_vector) for vertex in right_poly.vertices[:-1]])
	px = right_poly_x.mid.dot(x_vector) + rmin_x - depth_x/2

	# get "y"-component of collision point
	y_vector = Vec2d(-x_vector.y, x_vector.x)

	lmax_x = min([vertex.dot(x_vector) for vertex in left_poly.vertices[:-1]])

	left_filter = lambda vertex_point: abs((vertex_point - left_poly.mid).dot(x_vector) - lmax_x) < 1e-8
	right_filter = lambda vertex_point: abs((vertex_point - right_poly.mid).dot(x_vector) - rmin_x) < 1e-8

	left_points = list(filter(left_filter, left_poly.vertex_points[:-1]))
	right_points = list(filter(right_filter, right_poly.vertex_points[:-1]))

	if len(left_points) == 1:
		py = left_points[0].dot(y_vector)
	elif len(right_points) == 1:
		py = right_points[0].dot(y_vector)
	else:
		if sum(left_points).dot(y_vector) > sum(right_points).dot(y_vector):
			py = ((left_points[0] + right_points[0])/2).dot(y_vector)
		else:
			py = ((right_points[1] + left_points[1])/2).dot(y_vector)

	collision_point = px*x_vector + py*y_vector

	left_collision_vector = left_poly.mid - collision_point
	right_collision_vector = right_poly.mid - collision_point

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

	poly1 = Square(context, 0, 0, 1, 1, 0, 1)
	poly2 = Square(context, 0.75, 0.75, 1, 1, 0, 1)

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
	# left_poly, right_poly, collision_depth, collision_vector, left_collision_vector, right_collision_vector = collision_data
	# print(left_poly.mid, right_poly.mid)
	# print(left_collision_vector, right_collision_vector)
	#
	# spring_force = collision_vector*2000*collision_depth**(2/3)
	# print(spring_force)
	# print(left_collision_vector.cross(spring_force), right_collision_vector.cross(spring_force))
