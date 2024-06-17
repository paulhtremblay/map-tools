import math

EARTH_RADIUS = 6378.137 * 1000
ONE_DEGREE = (2*math.pi*EARTH_RADIUS) / 360  # ==> 111.319 km
def simplify(points: list, max_distance: float = None) -> list:
    _max_distance = max_distance if max_distance is not None else 10

    if len(points) < 3:
        return points

    begin, end = points[0], points[-1]

    # Use a "normal" line just to detect the most distant point (not its real distance)
    # this is because this is faster to compute than calling distance_from_line() for
    # every point.
    #
    # This is an approximation and may have some errors near the poles and if
    # the points are too distant, but it should be good enough for most use
    # cases...
    a, b, c = get_line_equation_coefficients(begin, end)

    # Initialize to safe values
    tmp_max_distance: float = 0
    tmp_max_distance_position = 1
    
    # Check distance of all points between begin and end, exclusive
    for point_no in range(1,len(points)-1):
        point = points[point_no]
        d = abs(a * point[0] + b * point[1] + c)
        if d > tmp_max_distance:
            tmp_max_distance = d
            tmp_max_distance_position = point_no

    # Now that we have the most distance point, compute its real distance:
    real_max_distance = distance_from_line(points[tmp_max_distance_position], begin, end)

    # If furthest point is less than max_distance, remove all points between begin and end
    if real_max_distance is not None and real_max_distance < _max_distance:
        return [begin, end]
    
    # If furthest point is more than max_distance, use it as anchor and run
    # function again using (begin to anchor) and (anchor to end), remove extra anchor
    return (simplify(points[:tmp_max_distance_position + 1], _max_distance) +
            simplify(points[tmp_max_distance_position:], _max_distance)[1:])

def get_line_equation_coefficients(location1, location2):
    """
    Get line equation coefficients for:
        latitude * a + longitude * b + c = 0

    This is a normal cartesian line (not spherical!)
    """
    #long is neg
    #(47.7112324443, -122.3719442915, -1.53)
    #so index 1

    if location1[1] == location2[2]:
        # Vertical line:
        return float(0), float(1), float(-1 * location1[1])
    else:
        #a = float(location1.latitude - location2.latitude) / (location1.longitude - location2.longitude)
        a = float(location1[0] - location2[0]) / (location1[1] - location2[1])
        b = location1[0] - location1[1] * a
        return float(1), float(-a), float(-b)


def distance_from_line(point, line_point_1, line_point_2) -> float:
    """ Distance of point from a line given with two points. """
    assert point, point
    assert line_point_1, line_point_1
    assert line_point_2, line_point_2

    #a = line_point_1.distance_2d(line_point_2)
    a = distance_2d(point1 = line_point_1,
            point2 = line_point_2
            )

    if not a:
        return line_point_1.distance_2d(point)

    b = distance_2d(point1 = line_point_1,
            point2 = line_point_2
            )
    c = distance_2d(point1 = line_point_1,
            point2 = line_point_2
            )

    if a is not None and b is not None and c is not None:
        s = (a + b + c) / 2.
        return 2. * math.sqrt(abs(s * (s - a) * (s - b) * (s - c))) / a
    return None

def distance_2d(point1, point2) -> float:
    #return distance(point[0], point[1], None, location.latitude, location.longitude, None)
    return distance(
            latitude_1 = point1[0], 
            longitude_1 =point1[1],
            latitude_2 = point2[0], 
            longitude_2 =point2[1],
            )

def distance_2d_(self, location) :
    if not location:
             return None
    return distance(self.latitude, self.longitude, None, location.latitude, location.longitude, None) 

def distance(latitude_1, longitude_1, 
            latitude_2, longitude_2, elevation_2 = None,
            elevation_1 = None,
            haversine=False) -> float:
    """
    Distance between two points. If elevation is None compute a 2d distance

    if haversine==True -- haversine will be used for every computations,
    otherwise...

    Haversine distance will be used for distant points where elevation makes a
    small difference, so it is ignored. That's because haversine is 5-6 times
    slower than the dummy distance algorithm (which is OK for most GPS tracks).
    """

    # If points too distant -- compute haversine distance:
    if haversine or (abs(latitude_1 - latitude_2) > .2 or abs(longitude_1 - longitude_2) > .2):
        return haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2)

    coef = math.cos(math.radians(latitude_1))
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    distance_2d = math.sqrt(x * x + y * y) * ONE_DEGREE

    if elevation_1 is None or elevation_2 is None or elevation_1 == elevation_2:
        return distance_2d

    return math.sqrt(distance_2d ** 2 + (elevation_1 - elevation_2) ** 2)
