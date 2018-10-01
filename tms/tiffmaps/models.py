from django.db import models


class SingletonMapSettings(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonMapSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class MapSettings(models.Model):
    google_maps_key = models.CharField(max_length=100, blank=True)
    default_centerx = models.FloatField(blank=True)
    default_centery = models.FloatField(blank=True)
    default_zoom = models.PositiveSmallIntegerField(default=12)

    def __str__(self):
        return str(self.google_maps_key)


class Overlay(models.Model):
    mapname = models.CharField(max_length=255, unique=True)
    extension = models.CharField(max_length=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    publish = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    minx = models.FloatField(blank=True)
    miny = models.FloatField(blank=True)
    maxx = models.FloatField(blank=True)
    maxy = models.FloatField(blank=True)
    centerx = models.FloatField(blank=True)
    centery = models.FloatField(blank=True)

    class Meta:
        ordering = ['mapname']

    def __str__(self):
        return str(self.mapname)