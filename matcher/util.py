from pprint import pprint
from polyline.codec import PolylineCodec
import requests
import urllib

OSRM_API_URL = 'http://localhost:5000'

def querystring_parts_from_geojson_geometry(geometry):
    yield ('compression', 'false')
    if geometry['type'] == 'LineString':

        # We have to fake the time because linestrings don't have timestamp data
        t = 0
        for pair in geometry['coordinates']:
            yield ('loc', '{},{}'.format(pair[0], pair[1]))
            yield ('t', t)
            t = t + 1

def get_polyline(geometry):
    def divide_by_ten(pairs):
        for pair in line:
            yield (pair[0] / 10, pair[1] / 10)

    line = PolylineCodec().decode(geometry)
    return list(divide_by_ten(line))

def get_osrm_match_data(geometry):
    qs = urllib.urlencode(list(querystring_parts_from_geojson_geometry(geometry)))
    url = '{}/match?{}'.format(OSRM_API_URL, qs)
    res = requests.get(url)
    data = res.json()
    return data

def get_matched_trace(geometry):
    data = get_osrm_match_data(geometry)

    # Silently ignore matches with multiple linestrings
    if len(data['matchings']) != 1:
        return None

    # Accept either compressed (polyline) or uncompressed (array of pairs)
    if isinstance(data['matchings'][0]['geometry'], basestring):
        line = get_polyline(data['matchings'][0]['geometry'])
    else:
        line = data['matchings'][0]['geometry']
    return line
