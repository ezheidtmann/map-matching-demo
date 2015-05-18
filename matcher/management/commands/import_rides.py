from django.core.management.base import BaseCommand

from itertools import tee, izip
import requests
from pprint import pprint
import hashlib
import json

# TODO: use jsonical

from ... import models, util

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        data = json.loads(open('trips.json').read())

        for feature in data['features']:
            feature_hash = hashlib.sha1(json.dumps(feature)).hexdigest()
            ride, created = models.Ride.objects.get_or_create(source_data_hash=feature_hash)
            ride.trace_json = json.dumps(feature['geometry'])
            matched_coords = util.get_matched_trace(feature['geometry'])
            if matched_coords is None:
                # Matching failed; let's move on to the next one
                continue

            matched_trace = {
                'coordinates': matched_coords,
                'type': 'LineString',
            }
            ride.matched_trace_json = json.dumps(matched_trace)
            ride.save()

            # Delete existing segment relations for this ride
            models.SegmentOrdering.objects.filter(ride=ride).delete()

            # SEGMENTZZ
            i = 0;
            for coord_pair in pairwise(matched_coords):
                kwargs = {
                    'lat_start': coord_pair[0][0],
                    'lng_start': coord_pair[0][1],
                    'lat_end':   coord_pair[1][0],
                    'lng_end':   coord_pair[1][1],
                }
                segment, created = models.Segment.objects.get_or_create(**kwargs)
                if created:
                    segment.update_reverse()
                models.SegmentOrdering.objects.create(ride=ride, segment=segment, position=i)
