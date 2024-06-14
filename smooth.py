import math
import numpy

Re = 6371000  # Earth radius in meters

def extract(point) :
    return (math.pi / 180 * point[0], math.pi / 180 * point[1])

# Compute the great circle distance between two points given in polar
# coordinates and radians. The return value is in the same units as
# Re is defined.
def dist(p0, p1) :
	a = math.sin((p1[0] - p0[0])/2)**2 + math.cos(p0[0]) * math.cos(p1[0]) * math.sin((p1[1] - p0[1])/2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return Re * c


def process(
        points, maxdistance = 5, maxinterval = 10, debug = False,
        verbose =False):
    bounds = (extract(points[0]), extract(points[-1]))
    if debug:
        print(f'bounds are {bounds}')
    idx,maxd = None,None
    for counter, i in enumerate(points):
        if counter == 0:
            continue
        current_points_in_radians = extract(i)
        if debug:
            print(f'this is {current_points_in_radians} and type is {type(current_points_in_radians)}')
        d = greatcircle_point_distance(bounds, current_points_in_radians)
        if debug:
            print(f'd is {d} and type is {type(d)}')
        if maxd is None or d > maxd :
            maxd = d
            idx = counter
        if debug:
            print(f'maxd is {maxd} and idx is {idx}')
    if maxd is not None and maxd  > maxdistance :
        # Keep this point if it is at least 'maxdistance' from the
        # connecting arc, and run 'process' on the two subsegments
        process(points[:idx], maxdistance, maxinterval)
        process(points[idx:], maxdistance, maxinterval)
    elif maxinterval is not None and maxinterval > 0 : #Python 3 fix                            
        prev = bounds[0]
        fin = bounds[1]
        for counter, i in enumerate(points):
            current_points_in_radians = extract(i)
            if dist(prev, current_points_in_radians) > maxinterval\
                and dist(fin, current_points_in_radians) > maxinterval :
                # Note that this does not satisfy the 'maxinterval' limit,
                # but instead takes the next point just further than the
                # given limit.
                # FIXME might be better to take the previous point, to make
                # the limit a guaranteed one.
                prev = current_points_in_radians
    return points


# Given a pair of polar coordinates and a third, find the shortest great circle
# distance from the third point to the great circle arc segment connecting
# the first two.
def greatcircle_point_distance(pair, third) :
	# Convert to cartesian coordinates for the vector math
	cpair = tuple( map(lambda pt: polcar(numpy.array(pt)), pair) )
	cthird = polcar(numpy.array(third))

	# Project 'third' onto the great circle arc joining 'pair' along the
	# vector that is normal to the chord between 'pair'
	normal = numpy.cross(*cpair)
	normal /= numpy.linalg.norm(normal)
	intersect = cthird - normal * numpy.dot(normal, cthird)
	intersect *= Re / numpy.linalg.norm(intersect)

	# Great circle distance from 'third' to its projection
	d = dist(third, carpol(intersect))

	# If the projection of 'third' is not between the shorter arc
	# connecting 'pair', we instead want the gc distance from 'third'
	# to the nearest of the two.
	d0 = numpy.dot(intersect, cpair[0])
	d1 = numpy.dot(intersect, cpair[1])
	c = numpy.dot(numpy.cross(intersect, cpair[0]), numpy.cross(intersect, cpair[1]))

	if c < 0 and ((d0 >= 0 and d1 >= 0) or  (d0 < 0 and d1 < 0)) :
		return d
	else :
		return min((dist(third, pair[0]), dist(third, pair[1])))

def polcar(polarpt) :
	lat,lon = polarpt
	# Quick sanity check
	assert lat > -2*math.pi and lat < 2*math.pi
	assert lon > -2*math.pi and lon < 2*math.pi
	xyz = (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))
	return Re * numpy.array(xyz)

# Convert from cartesian to polar coordinates, radians to units of Re
def carpol(xyz) :
	R = numpy.linalg.norm(xyz)
	# Quick sanity check
	assert (R-Re)*1.0/Re < 1e-14

	lat = math.asin(numpy.dot(numpy.array([0,0,1]), xyz) / R)

	xy = xyz.copy()
	xy[2] = 0
	xy /= numpy.linalg.norm(xy)
	lon = math.atan2(xy[1], xy[0])

	return numpy.array( (lat,lon) )
