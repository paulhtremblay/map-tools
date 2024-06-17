import os
import  math
from statistics import median
import kml
import gpx
import smooth
import pprint
pp = pprint.PrettyPrinter(indent = 4)

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

class ToolsError(Exception):
    pass

def haversine_distance(
    latitude_1: float, 
    longitude_1: float, 
    latitude_2: float, 
    longitude_2: float) -> float:    
    """
    Haversine distance between two points, expressed in meters.

    Implemented from http://www.movable-type.co.uk/scripts/latlong.html
    """
    EARTH_RADIUS = 6378.137 * 1000

    d_lon = math.radians(longitude_1 - longitude_2)
    lat1 = math.radians(latitude_1)
    lat2 = math.radians(latitude_2)
    d_lat = lat1 - lat2

    a = math.pow(math.sin(d_lat/2),2) + \
        math.pow(math.sin(d_lon/2),2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.asin(math.sqrt(a))
    d = EARTH_RADIUS * c

    return d

def reverse_points(points):
    points_ = [x for x in points]
    for i in reversed(points):
        points_.append(i)
    return points_

def create_mile_markers(points, 
        reverse = False,
        verbose = False):
    if reverse:
        points = reverse_points(points)
    total_distance = 0
    prev_point = None
    prev_mile = None
    miles = []
    for point in points:
        if not prev_point:
            prev_point = point
            continue
        dis =  haversine_distance(
            latitude_1 = prev_point[0], 
            longitude_1= prev_point[1], 
            latitude_2= point[0], 
            longitude_2= point[1])     
        total_distance += dis
        if prev_mile != None and math.floor(total_distance * 0.000621371) != prev_mile:
            mile_mark = math.floor(total_distance * 0.000621371)
            miles.append({'mile':mile_mark,
                'latitude':point[0],
                'longitude': point[1],
                'elevation': point[2]
                }
                    )
        prev_mile = math.floor(total_distance * 0.000621371)
        prev_point = point
    return miles


def find_nearest(point, points, verbose = False):
    nearest = (None, None)
    for counter, i in enumerate(points):
        distance = haversine_distance(
            latitude_1 =  point[0], 
            longitude_1 = point[1], 
            latitude_2 = i[0], 
            longitude_2 = i[1]    
        )
        if nearest[1] == None or distance < nearest[1]:
            nearest = (counter, distance)
    if verbose:
        pass
        #print(f'nearest is {nearest}')
    return nearest

def find_nearest_distance(point, points, distance, verbose = False):
    final = []
    for counter, i in enumerate(points):
        distance_ = haversine_distance(
            latitude_1 =  point[0], 
            longitude_1 = point[1], 
            latitude_2 = i[0], 
            longitude_2 = i[1]    
        )
        if distance_ == 0:
            continue
        elif distance_ <= distance:
            final.append(i)
    return final

def find_highest(points, verbose = False):
    highest = (None, None)
    for counter, i in enumerate(points):
        height = i[2]
        if height == None:
            continue
        if highest[1] == None or height > highest[1]:
            highest = (counter, height)
    return highest






def _get_median(points):
    lats = []
    longs = []
    for i in points:
        lats.append(i[0])
        longs.append(i[1])
    lats = sorted(lats)
    longs = sorted(longs)
    return median(lats), median (longs)


def _too_far(dis, max_ = 15):
    if dis < max_:
        return False
    return True

def merge_lines(tracks):
    points = []
    base_track = tracks[0][0]['points']
    final = []
    n_lons = []
    n_lats = []
    for p in base_track:
        temp_ = [p]
        for i in tracks[1:]:
            index, dist = find_nearest(p, i[0]['points'])
            if not _too_far(dist):
                temp_.append(i[0]['points'][index])
            n_lat, n_lon  = _get_median(points = temp_)
            final.append((n_lat, n_lon))
    for i in final:
        points.append((i[0], i[1], 0))
    return points

def tracks_from_file(path, verbose = False) -> object:
    ext = os.path.splitext(path)[1]
    if ext == '.gpx':
        tree = gpx.tracks_from_gpx(path = path, verbose = verbose)
    elif ext == '.kml':
        tree = kml.tracks_from_kml(path = path, verbose = verbose)
    else:
        raise ValueError('no match')
    return tree


def get_tree(path):
    with open(path, 'r') as read_obj:
        tree = etree.parse(read_obj)
    return tree

def write_to_path(root, path, verbose = False):
    s =  etree.tostring(root)
    with open(path, 'wb') as write_obj:
        write_obj.write(s)
    if verbose:
        print(f'wrote to {path}')


def combine_lines_to_one_file(paths, out, verbose = False):
    root = kml.make_write_root()
    folder =etree.Element("Folder") 
    root.append(folder)
    for path in paths:
        tracks = tracks_from_file(path = path)
        for track in tracks:
            line_el = kml.make_line(name = track['name'], 
                        points = track['points'])
            folder.append(line_el)
    write_to_path(
            root = root, 
            path = out, 
            verbose = verbose)

def convert_to_gpx(path, out, verbose = False):
    root = gpx.make_write_root()
    tracks = tracks_from_file(path = path)
    tree = get_tree(path = path)
    #TODO fix
    point_list = kml.get_points(
            tree = tree,
            verbose = verbose)
    for i in point_list:
        wpx = gpx.add_wpx(
                lattitude = i['points'][0], 
                longitude = i['points'][1], 
                elevation = i['points'][2],
                name = i['name'])
        root.append(wpx)
    for track in tracks:
        trk = gpx.make_trk_element(name = track['name'])
        root.append(trk)
        trkseg = gpx.make_trkseg(coordinates = track['points'])
        trk.append(trkseg)
    write_to_path(
            root = root, 
            path = out, 
            verbose = verbose)
        
def _get_cluster(point, points, max_):
    final = []
    for i in points:
        for j in i:
            dis = haversine_distance(
                latitude_1 = point[0] , 
                longitude_1= point[1], 
                latitude_2 =j[0]  , 
                longitude_2= j[1] )
            if dis <= max_:
                final.append((j[0], j[1]))
    return final

def mile_markers(path, out, reverse = False, verbose = False):
    root = kml.make_write_root()
    document_e =etree.Element("Document") 
    root.append(document_e)
    tracks = tracks_from_file(path = path)
    for track in tracks:
        points = track['points']
        miles = create_mile_markers(
                points = points, 
                reverse = reverse)
        for mile in miles:
            p =kml.make_point(
                    name = mile['mile'], 
                    latitude = mile['latitude'], 
                    longitude =  mile['longitude'], 
                    description = None,
                    elevation = mile['elevation'])
            document_e.append(p)
    write_to_path(
            root = root, 
            path = out,
            verbose = verbose)

def prune_by_location(
        points:list, 
        start:tuple = None, 
        end:tuple = None,
        verbose:bool = None):
    if start != None and end != None:
        raise ToolsError('must pass either start or end')
    if not start:
        start = 0
    else:
        n = find_nearest(
                point = start, 
                points = points, 
                verbose = verbose)
        start = n[0]
    if not end:
        end  = len(points) -1
    else:
        n = find_nearest(
                point = end, 
                points = points, 
                verbose = verbose)
        end = n[0]
    points = points[start:end]
    return points

def location_prune(
        path,
        out,
        start = None,
        end = None,
        verbose = False,
        line_name= 'new-line'
        ):
    l = tracks_from_file(
            path = path, 
            verbose = verbose)
    points = prune_by_location(
            points = l[0]['points'],
            start = start,
            end = end,
            verbose = verbose
            )
    root = kml.make_write_root()
    line_element = kml.make_line(name = line_name, points = points)
    root.append(line_element)
    write_to_path(root = root, path = out,verbose = verbose)

def convert_string_to_points(s):
    if s == None:
        return
    st, end = s.split(',')
    st = float(st)
    end = float(end)
    return st, end

def mult_lines_to_one(
        paths, 
        out, 
        verbose = False,
        line_name = 'new-line'
        ):
    points = []
    for path in paths:
        tracks = tracks_from_file(path = path)
        for track in tracks: 
            for i in track['points']:
                points.append(i)
    line_element = kml.make_line(
            name = line_name, points = points)
    root = kml.make_write_root()
    root.append(line_element)
    write_to_path(
            root = root, 
            path = out,
            verbose = verbose)

def polygon_from_files(
        paths,
        out,
        verbose = False,
        polygon_name = 'new-polygon'
        ):
    points = []
    for path in paths:
        tracks = tracks_from_file(path = path)
        for track  in  tracks:
            for j in track['points']:
                points.append(j)

    line_element = kml.make_polygon(
            name = polygon_name, 
            points = points, 
            verbose = verbose)
    root = kml.make_write_root()
    root.append(line_element)
    write_to_path(
            root = root, 
            path = out,
            verbose = verbose)

def prune_to_top(
        path,
        out,
        verbose = False,
        line_name= 'to-top'):
    l = tracks_from_file(path)
    assert len(l) == 1
    high_point =  find_highest(
            points = l[0]['points'], verbose = verbose)
    points = l[0]['points'][0:high_point[0]]
    line_element = kml.make_line(name = 'new-line', points = points)
    root = kml.make_write_root()
    root.append(line_element)
    write_to_path(
            root = root, 
            path = out,
            verbose = verbose)

def smooth_func(
        path,
        out, 
        verbose = False,
        line_name = 'smoothed-line'
        ):
    tracks = tracks_from_file(
            path = path, 
            verbose = verbose)
    assert len(tracks) == 1
    smoothed_points = smooth.process(
            points = tracks[0]['points'],
            verbose = verbose,
            maxdistance = 300, 
            maxinterval = 5,
            )
    line_element = kml.make_line(
            name = line_name, 
            points = smoothed_points
            )
    root = kml.make_write_root()
    root.append(line_element)
    write_to_path(root = root, 
            path = out,
            verbose = verbose)


def avg_points(points):
    prev_point = None
    dis = []
    for i in points:
        if not prev_point:
            prev_point = i
            continue
        d =  haversine_distance(
                latitude_1 =  prev_point[0], 
                longitude_1 = prev_point[1], 
                latitude_2 =  i[0], 
                longitude_2 =  i[1])     
        dis.append(d)
        prev_point = i
    return sum(dis)/len(dis),  median(dis)

def stats(
        path,
        verbose = False
        ):
    tracks = tracks_from_file(
            path = path, 
            verbose = verbose)
    for track in tracks:
        points = track['points']
        a = avg_points(points = points)

def get_within_distance(point, points, distance):
    final = []
    indices = []
    for point_ in points:
        d =  haversine_distance(
            latitude_1 =  point_[0], 
            longitude_1 =  point_[1], 
            latitude_2 =  point[0], 
            longitude_2 =  point[1])     
        if d <= distance:
            final.append(point_)
            indices.append(0)
    return final, indices

def get_new_current(clus, points):
    min_ = (None, None)
    for i in clus:
        for counter, j in enumerate(points):
            d =  haversine_distance(
                latitude_1 =  i[0], 
                longitude_1 =  i[1], 
                latitude_2 =  j[0], 
                longitude_2 =  j[1])     
            if min_[1] == None or d < min_[1]:
                min_ = (j, d)
    return min_[0]


def cluster_it(points, cluster_distance, max_iterations):
    final = []
    current = points[0]
    counter = 0
    temp_points = []
    for i in points:
        temp_points.append(i)
    while 1:
        counter += 1
        counter2 = 0
        while 1:
            counter2 += 1
            clus, indices = get_within_distance(
                    point = current,
                    points = temp_points,
                    distance = cluster_distance * counter2
                    )
            if len(clus) > 0:
                break
            else:
                print('did not find cluster, trying again')
            if counter2 > 10:
                raise ValueError('tried 10 times and could not find cluster')
        final.append(clus)
        temp = []
        for i in temp_points:
            if i in clus:
                continue
            temp.append(i)
        temp_points = temp
        n_current = get_new_current(clus, temp_points)
        if not n_current:
            return final, temp_points, current
        d_temp =  haversine_distance(
                latitude_1 =  n_current[0], 
                longitude_1 =  n_current[1], 
                latitude_2 =  current[0], 
                longitude_2 =  current[1])     
        #print(f'dis between old and new is {d_temp}')
        if d_temp > 1000:
            return final, temp_points, current
        current = n_current
        if current in clus:
            assert False
        if counter == max_iterations or len(temp_points) == 0:
            break

    return final, temp_points, current

def med_of_clusters(clusters):
    final = []
    for i in clusters:
        lat, lon = _get_median(i)
        final.append((lat, lon, 0))
    return final

def cluster(path,
        verbose = False
        ):
    tracks = tracks_from_file(
            path = path, 
            verbose = verbose)
    assert len(tracks) == 1
    points = tracks[0]['points']
    clusters, remaining, next_ = cluster_it(
            points = points,
            cluster_distance = 50,
            max_iterations = 200)
    meds = med_of_clusters(clusters)
    return clusters, meds, remaining, next_
