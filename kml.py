try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

import tools

class KmlError(Exception):
    pass

def swap_long_lat(points):
    """
    for kml
    """
    final = []
    for i in points:
        if len(i) == 3:
            final.append((i[1], i[0], i[2]))
        else:
            final.append((i[1], i[0]))
    return final


def tracks_from_file(path, verbose = False):
    ext = os.path.splitext(path)[1]
    if ext == '.gpx':
        tree = tracks_from_gpx(path = path, verbose = verbose)
    elif ext == '.kml':
        tree = tracks_from_kml(path = path, verbose = verbose)
    else:
        raise ValueError('no match')
    return tree



def tracks_from_kml(path, verbose = False):
    tree = tools.get_tree(path = path)
    lines = get_lines(tree= tree)
    final = []
    for counter, i in enumerate(lines):
        name = i['name']
        d = {'name':name, 'points':i['points']}
        
        final.append(d)
    return final

def make_write_root()-> object:
    root = etree.Element("kml", 
            xmlns= "http://www.opengis.net/kml/2.2")
    return root

def make_point(
        name, 
        latitude, 
        longitude, 
        description = None,
        elevation = 0):
    placemark = etree.Element("Placemark")
    if description:
        description_e =etree.Element("description") 
        description_e.text = description
        placemark.append(description_e)
    point =etree.Element("Point") 
    name_e =etree.Element("name") 
    name_e.text = str(name)
    coordinates =etree.Element("coordinates") 
    coordinates.text = f"{longitude},{latitude},{elevation}"
    point.append(coordinates)
    placemark.append(point)
    placemark.append(name_e)
    return placemark

def make_line(name, points):
    points = swap_long_lat(points)
    placemark = etree.Element("Placemark")
    name_e =etree.Element("name") 
    name_e.text = name
    placemark.append(name_e)
    line_string =etree.Element("LineString") 
    extrude = etree.Element("extrude") 
    extrude.text = '1'
    line_string.append(extrude)
    tessellate = etree.Element("tessellate") 
    tessellate.text = '1'
    line_string.append(tessellate)
    coordinates = etree.Element("coordinates") 
    coordinates_string = make_point_strings(points)
    coordinates.text = coordinates_string
    line_string.append(coordinates)
    placemark.append(line_string)
    return placemark

def make_point_strings(points):
    if isinstance(points, str):
        return points
    coordinates_list = []
    for i in points:
        if len(i) == 3:
            coordinates_list.append(f'{i[0]},{i[1]},{i[2]}')
        else:
            coordinates_list.append(f'{i[0]},{i[1]}')
    coordinates_string = '\n'.join(coordinates_list)
    return coordinates_string


def get_lines(tree:object)->list:
    final = []
    l = tree.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
    for i in l:
        children = list(i)
        name = None
        for j in children:
            if j.tag == '{http://www.opengis.net/kml/2.2}name':
                name  = j.text
            elif j.tag == '{http://www.opengis.net/kml/2.2}LineString':
                for k in list(j):
                    if k.tag == '{http://www.opengis.net/kml/2.2}coordinates':
                        points = _get_points_from_line_string(k.text)
                        if name == None:
                            assert False
                        final.append(
                                {'name':name, 
                                    'points': points
                                    })
    return final

def _get_points_from_line_string(s):
    final = []
    for i in s.split('\n'):
        if i.strip() == '':
            continue
        lat, lon, ele =  get_cooridinates_from_string(s= i)
        final.append((float(lat), float(lon), float(ele)))
    return final

def get_cooridinates_from_string(s:str)->(str, str, str):
    s = s.strip()
    fields = s.split(',')
    if len(fields) < 2:
        raise KmlToGpxError('not enough fields in coordinates')
    elevation = None
    if len(fields) == 3:
        elevation = float(fields[2])
    return float(fields[1]), float(fields[0]), elevation

def make_polygon(
        name: str,
        points: list,
        verbose: bool,
        )-> object:
    points = swap_long_lat(points)
    placemark_e = etree.Element("Placemark")
    name_e =etree.Element("name") 
    name_e.text = name
    polygon_e =etree.Element("Polygon") 
    placemark_e.append(name_e)
    placemark_e.append(polygon_e)
    outerBoundaryIs_e =etree.Element("outerBoundaryIs") 
    polygon_e.append(outerBoundaryIs_e)
    LinearRing_e =etree.Element("LinearRing") 
    tessellate_e =etree.Element("tessellate") 
    tessellate_e.text = "1"
    LinearRing_e.append(tessellate_e)
    coordinates_e =etree.Element("coordinates") 
    if points[0] != points[-1]:
        points.append(points[0])
    coordinates_e.text =  make_point_strings(points)
    LinearRing_e.append(coordinates_e)
    outerBoundaryIs_e.append(LinearRing_e)
    return placemark_e
          

def get_points(tree:object, verbose = False)-> list:
    final = []
    l =  tree.findall('.//{http://www.opengis.net/kml/2.2}Placemark')  
    for i in l:
        is_linestring = False
        children = list(i)
        for j in children:
            if j.tag == '{http://www.opengis.net/kml/2.2}LineString':
                is_linestring = True
        if not is_linestring:
            l_cooridinates =  i.findall('{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')  
            l_name =  i.findall('{http://www.opengis.net/kml/2.2}name')  
            cooridinates = get_cooridinates_from_string(
                    s = l_cooridinates[0].text)
            name = None
            if l_name:
                name =l_name[0].text
            final.append({'name':name, 'points':cooridinates})
    return final

