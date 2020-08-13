import random
import numpy as np
from time import time
from square import Square
from vector2 import Vec2d
from polygon import Polygon

def get_collision_depth(poly1, poly2, n):
	between_vec = poly1.mid - poly2.mid
	between = between_vec.dot(n)
	if between < 0:
		between *= -1
		left_poly = poly2
		right_poly = poly1
	else:
		left_poly = poly1
		right_poly = poly2

	max_l2n = min([vertex.dot(n) for vertex in left_poly.vertices[:-1]])
	min_l2n = max([vertex.dot(n) for vertex in right_poly.vertices[:-1]])

	return (between - min_l2n + max_l2n)*-1, left_poly, right_poly

def get_poly_circle_collision_depth(poly, point, radius, n):
	between_vec = poly.mid - point
	between = between_vec.dot(n)
	if between < 0:
		between *= -1
		# poly is left, point is right
		max_l2n = min([vertex.dot(n) for vertex in poly.vertices[:-1]])
		min_l2n = radius
	else:
		# point is left, poly is right
		max_l2n = -radius
		min_l2n = max([vertex.dot(n) for vertex in poly.vertices[:-1]])

	return (between - min_l2n + max_l2n)*-1


def get_collision_vectors(left_poly, right_poly, collision_vector):
	# get all collision polygon vertex points
	colypoly_vertex_points = []

	for point in left_poly.vertex_points[:-1]:
		if point_in_polygon(point, right_poly):
			colypoly_vertex_points.append(point.copy())

	for point in right_poly.vertex_points[:-1]:
		if point_in_polygon(point, left_poly):
			colypoly_vertex_points.append(point.copy())

	for edge1 in left_poly.edges:
		for edge2 in right_poly.edges:
			P1 = edge1[0] + left_poly.mid
			r1 = edge1[1] - edge1[0]
			P2 = edge2[0] + right_poly.mid
			r2 = edge2[1] - edge2[0]

			denominator = r1.cross(r2)
			if denominator == 0:
				continue

			t1 = (r2.cross(P1) - r2.cross(P2))/denominator
			t2 = (r1.cross(P1) - r1.cross(P2))/denominator

			if 0 <= t1 <= 1 and 0 <= t2 <= 1:
				P = P1 + r1*t1
				colypoly_vertex_points.append(P)

	# sort collision vertex points so the points are in a clockwise ordering
	pseudo_mid = sum(colypoly_vertex_points)/len(colypoly_vertex_points)
	colypoly_vertex_points.sort(key=lambda point: (point - pseudo_mid).angle, reverse=True)

	# the center of the collision polygon is the point where the collision occurred
	collision_point = get_polygon_mid(colypoly_vertex_points)

	left_collision_vector = left_poly.mid - collision_point
	right_collision_vector = right_poly.mid - collision_point

	return left_collision_vector, right_collision_vector

def point_in_polygon(point, polygon):
	for normal in polygon.normals:
		if get_poly_circle_collision_depth(polygon, point, 0, normal) < 0:
			return False
	return True

def get_polygon_mid(vertex_points):
	n = len(vertex_points) - 1

	if n == 1:
		return (vertex_points[0] + vertex_points[1])/2
	elif n == 0:
		return vertex_points[0]

	P0 = vertex_points[0]

	total_area = 0
	midpoints = Vec2d(0, 0)
	for i in range(1, n):
		Pi, Pii = vertex_points[i], vertex_points[i+1]

		area = abs((Pi - P0).cross(Pii - P0))
		total_area += area
		midpoints += ((P0 + Pi + Pii)/3)*area

	if total_area == 0:
		print(midpoints, vertex_points, n)

	return midpoints/total_area

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
