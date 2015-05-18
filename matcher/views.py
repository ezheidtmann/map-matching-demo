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

def _iter_segments_geojson_features(segments):
    for segment in segments:
        if segment.num_rides <= 1:
            continue

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
                'ride_count': segment.num_rides,
            },
        }

def segments(request):
    from django.db.models import Count
    segments = models.Segment.objects.annotate(num_rides=Count('segmentordering'))
    data = list(_iter_segments_geojson_features(segments))

    return JsonResponse({ 'features': data, 'type': 'FeatureCollection' })
