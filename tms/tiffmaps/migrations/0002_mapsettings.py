# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_settings(apps, schema_editor):
	MapSettings = apps.get_model("tiffmaps", "MapSettings")
	db_alias = schema_editor.connection.alias
	MapSettings.objects.using(db_alias).bulk_create([
		MapSettings(
			google_maps_key = "",
			default_centerx = 0,
			default_centery = 0,
			default_zoom = 3,
		),
	])


class Migration(migrations.Migration):

    dependencies = [
        ('tiffmaps', '0001_initial'),
    ]

    operations = [
    	migrations.RunPython(load_settings),
]
