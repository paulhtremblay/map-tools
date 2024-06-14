try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

class KmlToGpxError(Exception):
    pass
import tools

def tracks_from_gpx(path, verbose = False):
    tree = tools.get_tree(path = path)
    trk =   tree.findall('.//{http://www.topografix.com/GPX/1/1}trk')  
    final = []
    for counter, i in enumerate(trk):
        name = f'track_{counter}'
        for j in i.iter('{http://www.topografix.com/GPX/1/1}name'):
            name = j.text
        d = {'name':name, 'points':[]}
        trksegs = i.findall('{http://www.topografix.com/GPX/1/1}trkseg')
        for j in trksegs:
            trackpoints = j.findall('{http://www.topografix.com/GPX/1/1}trkpt')
            for trackpoint in trackpoints:
                ele = trackpoint.findall('{http://www.topografix.com/GPX/1/1}ele')
                elevation = 0
                if ele:
                    elevation = float(ele[0].text)
                d['points'].append((float(trackpoint.get('lat')), float(trackpoint.get('lon')), elevation))
        final.append(d)
    return final

def make_write_root()-> object:
    root = etree.Element("gpx", 
            creator = "GPSMAP 64st", version = "1.1", xmlns= "http://www.topografix.com/GPX/1/1")
    return root

def add_wpx(lattitude, longitude, name, elevation = None):
    wpt = etree.Element("wpt", lat=str(lattitude), lon=str(longitude))
    if elevation:
        ele = etree.Element("ele")
        ele.text = str(elevation)
    name_element = etree.Element("name")
    name_element.text = name
    sym = etree.Element("sym")
    sym.text = "Residence"

    if elevation:
        wpt.append(ele)
    wpt.append(name_element)
    wpt.append(sym)
    return wpt


def make_trkpt(lattitude:float, longitude:float, elevation:float)->object:
    trkpt = etree.Element("trkpt", lat=str(lattitude), lon = str(longitude) )
    if elevation:
        ele = etree.Element("ele")
        ele.text = str(elevation)
        trkpt.append(ele)
    return trkpt

def make_trk_element(name):
    trk = etree.Element("trk")
    if name:
        name_element = etree.Element("name")
        name_element.text = name
        trk.append(name_element)
    return trk


def make_trkseg(coordinates:str)->object:
    trkseg = etree.Element("trkseg")
    for i in coordinates:
        trkpt = make_trkpt(
                lattitude =i[0],
                longitude = i[1],
                elevation = i[2],
                )
        trkseg.append(trkpt)
    return trkseg

