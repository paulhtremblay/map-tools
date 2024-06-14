import os
import argparse
import pprint
import math
#from statistics import median

import smooth as smooth
import kml
import tools
import gpx


pp = pprint.PrettyPrinter(indent= 4)

class KmlToGpxError(Exception):
    pass

def _get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                   description='valid subcommands',
                                   help='additional help')

    parser_combine_files = subparsers.add_parser('combine-files', 
            help='combine lines from mult files into one or more lines in one file')
    parser_combine_files.add_argument("--verbose", '-v',  action ='store_true')  
    parser_combine_files.set_defaults(func=combine_files)
    parser_combine_files.add_argument("paths", nargs='+', help="path of file")
    parser_combine_files.add_argument("--out", '-o',  required = True, help="out-path")

    parser_convert_gpx = subparsers.add_parser('convert-to-gpx', help='convert to gpx')
    parser_convert_gpx.set_defaults(func=convert_to_gpx)
    parser_convert_gpx.add_argument("path", help="path of file")
    parser_convert_gpx.add_argument("--verbose", '-v',  action ='store_true')  
    parser_convert_gpx.add_argument("--out", "-o", required = False,  
            help="out path of file")

    parser_combine_diff_lines = subparsers.add_parser(
            'merge-lines', help='merge paths')
    parser_combine_diff_lines.add_argument("paths", nargs='+', help="path of file")
    parser_combine_diff_lines.add_argument("--verbose", '-v',  action ='store_true')  
    parser_combine_diff_lines.add_argument("--out", required = True,  
            help="out path of file")
    parser_combine_diff_lines.set_defaults(func=merge_lines)

    parser_create_mile_markers = subparsers.add_parser(
            'mile-markers', help='create mile markers')
    parser_create_mile_markers.add_argument("--verbose", '-v',  action ='store_true')  
    parser_create_mile_markers.set_defaults(func=create_mile_markers)
    parser_create_mile_markers.add_argument("path", help="path of file")
    parser_create_mile_markers.add_argument("--out", required = True,  
            help="out path of file")
    parser_create_mile_markers.add_argument("--reverse", '-r',  
            action ='store_true', help = 'route is up and back, so double points')  

    parser_prune_by_mark = subparsers.add_parser(
            'prune-by-location', help='prune by location')
    parser_prune_by_mark.add_argument("--verbose", '-v',  action ='store_true')  
    parser_prune_by_mark.add_argument("path", help="path of file")
    parser_prune_by_mark.add_argument("--start", '-s',  type = str, help = 'strart location')  
    parser_prune_by_mark.add_argument("--end", '-e',  type = str, help = 'strart location')  
    parser_prune_by_mark.set_defaults(func=prune_by_location)

    parser_files_to_line = subparsers.add_parser(
            'files-to-line', 
            help='use multpile files to create one line')
    parser_files_to_line.add_argument("paths", nargs='+', help="path of file")
    parser_files_to_line.add_argument("--out", required = True,  
            help="out path of file")
    parser_files_to_line.add_argument("--verbose", '-v',  action ='store_true')  
    parser_files_to_line.set_defaults(func=files_to_lines)

    parser_prune_to_top = subparsers.add_parser(
            'prune-to-top', help='prune just the first half of hike')
    parser_prune_to_top.add_argument("--verbose", '-v',  action ='store_true')  
    parser_prune_to_top.add_argument("path", help="path of file")
    parser_prune_to_top.set_defaults(func=prune_to_top)

    parser_polygon_from_files = subparsers.add_parser(
            'polygon-from-files', 
            help='use multpile files to create one polygon')
    parser_polygon_from_files.add_argument("paths", nargs='+', help="path of file")
    parser_polygon_from_files.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    parser_polygon_from_files.add_argument("--verbose", '-v',  action ='store_true')  
    parser_polygon_from_files.set_defaults(func=polygon_from_files)

    parser_smooth = subparsers.add_parser(
            'smooth', 
            help='smooth')
    parser_smooth.add_argument("--verbose", '-v',  action ='store_true')  
    parser_smooth.add_argument("path", help="path of file")
    parser_smooth.set_defaults(func=smooth_func)
    

    args = parser.parse_args()
    args.func(args)

    return args



def get_waypoint_info_from_element(placemark:object) -> (str,str):
    name = None
    coordinates = None
    for element in placemark.iter():
        if element.tag == '{http://www.opengis.net/kml/2.2}name':
            if name != None:
                raise KmlToGpxError('more than one point in element; don\'t know how to handle')
            name = element.text
        elif element.tag == '{http://www.opengis.net/kml/2.2}coordinates':
            if coordinates != None:
                print(coordinates)
                raise KmlToGpxError('more than one point in element; don\'t know how to handle')
            coordinates = element.text.strip()

    return name, coordinates



def get_cooridinates_from_lines(line_list):
    assert False, 'do not use'
    l =   []
    for i in line_list:
        l.append(i.text.strip())
    return '\n'.join(l)

def combine_lines(root_or_path):
    assert False, 'use files-to-line'
    if isinstance(root_or_path, str):
        root = get_tree(root_or_path)
    else:
        root = root_or_path
    lines = get_lines(tree = root)
    s= get_cooridinates_from_lines(line_list = lines)
    line_el = make_line(name = 'combined-line', 
            points = s)
    root = make_write_root()
    root.append(line_el)
    return root


def main():
    args = _get_args()


def combine_files(args):
    tools.combine_lines_to_one_file(
            paths = args.paths,
            out = args.out,
            verbose = args.verbose
            )


def _make_out_path(path):
    dir_ = os.path.dirname(os.path.abspath(path))
    rel_in_path = os.path.split(path)[1]
    rel_in_path_no_ext = os.path.splitext(rel_in_path)[0]
    out_path = os.path.join(dir_, f'{rel_in_path_no_ext}_combined.kml')
    return out_path

def _make_out_path_gen(path, ext, name = '', ):
    dir_ = os.path.dirname(os.path.abspath(path))
    rel_in_path = os.path.split(path)[1]
    rel_in_path_no_ext = os.path.splitext(rel_in_path)[0]
    out_path = os.path.join(dir_, f'{rel_in_path_no_ext}{name}.{ext}')
    return out_path

def _make_points_from_lines(line_list):
    assert False, 'not used'
    final = []
    for i in line_list:
        for element in i.iter():
            if element.tag == '{http://www.opengis.net/kml/2.2}coordinates':
                coordinates = element.text.strip()
                for j in coordinates.split('\n'):
                    pairs = get_cooridinates_from_string(s = j)
                    pairs = (pairs[1], pairs[0], pairs[2])
                    final.append(pairs)
    final = sorted(final, key = lambda x:x[0])
    longitude = [x[0] for x in final]
    latitude = [x[1] for x in final]
    return longitude, latitude

def combine(args):
    in_path = args.path
    root = combine_lines(root_or_path = in_path)
    write_to_path(root = root, path = _make_out_path(in_path))

def convert_to_gpx(args):
    tools.convert_to_gpx(path = args.path, 
            verbose = args.verbose,
            out = args.out)
    return
    tree = get_tree(path = args.path)
    line_list = get_lines(tree)
    point_list = get_points(tree = tree)
    write_root = make_write_root_gpx()
    for i in point_list:
        name, coordinates  = get_waypoint_info_from_element(
                placemark = i)
        lattitude, longitude, elevation = get_cooridinates_from_string(coordinates)
        add_wpx(root = write_root, lattitude = lattitude, 
            longitude = longitude, name = name, elevation = elevation)
    trk = make_trk(root = write_root)
    for i in line_list:
        trkseg = make_trkseg(trk = trk, coordinates = i)
        trk.append(trkseg)
    out = args.out
    if not args.out:
       out = _make_out_path_gen(path = args.path, ext = 'gpx' )
    write_to_path(root = write_root, path = out,verbose = args.verbose)

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

def merge_lines(args):
    tracks = []
    for path in args.paths:
        tracks.append(tracks_from_file(path = path, verbose = args.verbose))
    points = tools.merge_lines(tracks = tracks)
    new_line_element = make_line(name = 'averaged-line', points = points)
    root = make_write_root()
    root.append(new_line_element)
    out = args.out
    write_to_path(root = root, path = out,verbose = args.verbose)

def merge_lines_cluster(args):
    tracks = []
    for path in args.paths:
        ext = os.path.splitext(path)[1]
        if ext == '.gpx':
            tracks.append(tracks_from_gpx(path))
    points = [tracks[x][0]['points'] for x in range(len(tracks))]
    f = []
    for i in points[0]:
        c = _get_cluster(
                point = i,
                points = points,
                max_ = 25
                )
        f.append(_get_median(
                points = c
                ))
    points_ = []
    for i in f:
        points_.append((i[1], i[0], 0))
    root = make_write_root()
    new_line_element = make_line(name = 'averaged-line', points = points_)
    root.append(new_line_element)
    #out = _make_out_path_gen(path = args.path, ext = 'kml', name = '_smoothed' )
    out = '/home/henry/Downloads/averaged2.kml'
    write_to_path(root = root, path = out,verbose = args.verbose)

"""
These are GPX functions
"""

#distance

def calc_distance(origin, destination):
    """great-circle distance between two points on a sphere
       from their longitudes and latitudes"""
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km. earth

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = (sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dlon/2) * sin(dlon/2))
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c

    return d

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

def create_mile_markers(args):
    l = tracks_from_kml(path = args.path)
    root = make_write_root()
    document_e =etree.Element("Document") 
    root.append(document_e)
    for i in l:
        points = i['points']
        miles = tools.create_mile_markers(
                points = points, 
                reverse = args.reverse)
        for mile in miles:
            p =make_point(
                    name = mile['mile'], 
                    latitude = mile['latitude'], 
                    longitude =  mile['longitude'], 
                    description = None,
                    elevation = mile['elevation'])
            document_e.append(p)

    write_to_path(root = root, path = args.out,verbose = args.verbose)

def _convert_string_to_points(s):
    st, end = s.split(',')
    st = float(st)
    end = float(end)
    return st, end

def prune_by_location(args):
    l = tracks_from_file(path = args.path, verbose = args.verbose)
    assert len(l) ==1
    points = kml.prune_by_location(
            points = l[0]['points'],
            start = args.start,
            end = args.end,
            verbose = args.verbose
            )
    root = make_write_root()
    line_element = make_line(name = 'new-line', points = points)
    root.append(line_element)
    out = _make_out_path_gen(path = args.path, ext = 'kml', name = '_pruned' )
    write_to_path(root = root, path = out,verbose = args.verbose)

def files_to_lines(args):
    points = []
    for i in args.paths:
        tracks = tracks_from_kml(path = i)
        for track in tracks: 
            for i in track['points']:
                points.append(i)
    line_element = make_line(name = 'new-line', points = points)
    root = make_write_root()
    root.append(line_element)
    write_to_path(root = root, path = args.out,verbose = args.verbose)


def prune_to_top(args):
    l = tracks_from_file(args.path)
    assert len(l) == 1
    high_point =  tools.find_highest(
            points = l[0]['points'], verbose = args.verbose)
    points = l[0]['points'][0:high_point[0]]
    line_element = make_line(name = 'new-line', points = points)
    root = make_write_root()
    root.append(line_element)
    out = _make_out_path_gen(path = args.path, ext = 'kml', name = '_highest' )
    write_to_path(root = root, path = out,verbose = args.verbose)

def polygon_from_files(args):
    points = []
    for i in args.paths:
        tracks = tracks_from_kml(path = i)
        for track  in  tracks:
            for j in track['points']:
                points.append(j)

    line_element = make_polygon(
            name = 'new-line', points = points, verbose = args.verbose)
    root = make_write_root()
    root.append(line_element)
    write_to_path(root = root, path = args.out,verbose = args.verbose)

def smooth_func(args):
    tracks = tracks_from_file(
            path = args.path, 
            verbose = args.verbose)
    assert len(tracks) == 1
    smoothed_points = smooth.process(
            points = tracks[0]['points'],
            verbose = args.verbose
            )
    line_element = make_line(name = 'smoothed-line', points = smoothed_points)
    root = make_write_root()
    root.append(line_element)
    out = _make_out_path_gen(path = args.path, ext = 'kml', name = '_smoothed' )
    write_to_path(root = root, path = out,verbose = args.verbose)


if __name__== '__main__':
    main()
