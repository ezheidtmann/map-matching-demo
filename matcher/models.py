from django.db import models

# Create your models here.
#

class Segment(models.Model):
    lat_start = models.FloatField()
    lng_start = models.FloatField()

    lat_end = models.FloatField()
    lng_end = models.FloatField()

    reverse_segment = models.ForeignKey('Segment', null=True)

    def update_reverse(self):
        reverse_kwargs = {
            'lat_start': self.lat_end,
            'lng_start': self.lng_end,
            'lat_end':   self.lat_start,
            'lng_end':   self.lng_start,
        }
        try:
            self.reverse_segment = Segment.objects.get(**reverse_kwargs)
        except Segment.DoesNotExist:
            return

        self.save()

        if self.reverse_segment.reverse_segment is None:
            self.reverse_segment.reverse_segment = self
            self.reverse_segment.save()


    class Meta:
        unique_together = (
            ('lat_start', 'lng_start', 'lat_end', 'lng_end'),
        )


class SegmentOrdering(models.Model):
    ride = models.ForeignKey('Ride')
    segment = models.ForeignKey('Segment')
    position = models.IntegerField()


class Ride(models.Model):
    trace_json = models.TextField(null=True)
    matched_trace_json = models.TextField(null=True)
    segments = models.ManyToManyField(Segment)

    source_data_hash = models.CharField(max_length=160, unique=True)
