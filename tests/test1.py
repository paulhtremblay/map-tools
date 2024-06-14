import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURRENT_DIR)
ONE_UP = os.path.split(CURRENT_DIR)[0]
sys.path.append(ONE_UP)

import pprint
pp = pprint.PrettyPrinter(indent = 4)


import kml
import gpx
import tools

def _write(root, path):
    dir_ = os.path.dirname(os.path.abspath(__file__))
    dir2 = os.path.join(dir_, 'test_out')
    if not os.path.isdir(dir2):
        os.mkdir(dir2)
    path = os.path.join(dir2,  path)
    tools.write_to_path(root = root, path = path)


def test_point():
    root = kml.make_write_root()
    p = kml.make_point(
            name = 'test_point', 
            latitude = 37.42228990140251, 
            longitude = -122.0822035425683, 
            description = 'pytest test' )
    root.append(p)
    _write(root = root, path = 'test_point_ex1.kml')

def test_line1():
    root = kml.make_write_root()
    points = [   (47.65846, -122.40767, 0),
    (47.65859, -122.4075, 0),
    (47.6586, -122.40749, 0),
    (47.6586, -122.40748, 0),
    (47.65867, -122.40745, 0)]

    l = kml.make_line(
            name = 'test-line',
            points = points
            )
    root.append(l)
    _write(root = root, path = 'test_line_ex1.kml')

def test_get_tree():
    path = os.path.join(CURRENT_DIR, 'test_data', 'mult_lines1.kml')
    root = tools.get_tree(path = path)

def test_get_lines():
    path = os.path.join(CURRENT_DIR, 'test_data', 'mult_lines1.kml')
    root = tools.get_tree(path = path)
    lines = kml.get_lines(tree = root)
    assert len(lines) == 2
    assert lines[0]['name'] == 'name-of-line1'

def test_get_lines_from_kml():
    path = os.path.join(CURRENT_DIR, 'test_data', 'mult_lines1.kml')
    lines = kml.tracks_from_kml(path = path, verbose = False)
    assert len(lines) == 2
    assert lines[0]['name'] == 'name-of-line1'


def test_get_lines_from_gpx():
    path = os.path.join(CURRENT_DIR, 'test_data', 'test1.gpx')
    lines = gpx.tracks_from_gpx(path, verbose = False)
    assert len(lines) == 2
    assert lines[0]['name'] == 'Barrett Spur 1'

def test_prune_by_location():
    path = os.path.join(CURRENT_DIR, 'test_data', 'fourty_eight_st.kml')
    #lines = kml_tools.tracks_from_kml(path, verbose = False)
    lines = tools.tracks_from_file(
            path = path, 
            verbose = False)
    points = lines[0]['points']
    points = kml.prune_by_location(
        points = points, 
        start = None, 
        end = (47.58124, -122.39294)
        )
    assert len(points) == 3
    root = kml.make_write_root()
    l = kml.make_line(
            name = 'test-line',
            points = points
            )
    root.append(l)
    _write(root = root, path = 'test_prune_by_location.kml')

def test_get_points():
    path = os.path.join(CURRENT_DIR, 'test_data', 'mult_lines_points.kml')
    tree = tools.get_tree(path)
    points = kml.get_points(tree)
    assert len(points) == 2
    assert points[0]['name'] == 'wp1'
