import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ONE_UP = os.path.split(CURRENT_DIR)[0]
sys.path.append(ONE_UP)

import pprint
pp = pprint.PrettyPrinter(indent = 4)


import kml
import gpx
import tools

def test_stats():
    tools.stats(
            path = 'tests/test_data/test2.gpx'
            )

def test_cluster():
    points = tools.cluster(path = 'tests/test_data/test2.gpx' 
            )
    root = kml.make_write_root()
    folder =etree.Element("Folder") 
