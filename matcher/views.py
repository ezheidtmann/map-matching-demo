from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import JsonResponse

from . import models

# Create your views here.
def map(request):
    return TemplateResponse(request, 'map.html')


def _iter_lowest_pk_segments(segments):
    for segment in segments:
        pk = segment.pk
        if segment.reverse_segment is not None:
            reverse_pk = segment.reverse_segment.pk
            if pk < reverse_pk:
                yield segment
            else:
                yield segment.reverse_segment
        else:
            yield segment

from django.contrib.gis.geos import Point, Polygon
bbox = [[[-122.6706234025,45.5075409944],[-122.6706234025,45.5142323622],[-122.6642643845,45.5142323622],[-122.6642643845,45.5075409944],[-122.6706234025,45.5075409944]]]

def make_bounds(bbox_geojson):
    lats = [p[1] for p in bbox[0]]
    lngs = [p[0] for p in bbox[0]]
    return Polygon.from_bbox((min(lats), min(lngs), max(lats), max(lngs)))


def _iter_segments_geojson_features(segments):
    bounds = make_bounds(bbox)
    for segment in segments:
        #if not bounds.prepared.contains(Point(segment.lat_start, segment.lng_start)):
        #    continue;

        yield {
            'type': 'Feature',
            'geometry': {
                'coordinates': [
                    [ segment.lng_start, segment.lat_start ],
                    [ segment.lng_end,   segment.lat_end ],
                ],
                'type': 'LineString',
            },
            'properties': {
                'segment_pk': segment.pk,
                'ride_count': segment.ride_count,
                'rides': [ so.ride.pk for so in segment.segmentordering_set.all() ],
            },
        }

from django.views.decorators.cache import cache_page

@cache_page(60 * 60 * 12)
def segments(request):
    from django.db.models import Count
    segments = models.Segment.objects.annotate(ride_count=Count('segmentordering')).filter(ride_count__gt=1)
    segments = segments.prefetch_related('segmentordering_set__ride')
    data = list(_iter_segments_geojson_features(segments))

    return JsonResponse({ 'features': data, 'type': 'FeatureCollection' })
