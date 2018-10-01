from django import forms
from .models import (
    Overlay,
    MapSettings,
)


class MapSettingsForm(forms.Form):
    google_maps_key = forms.CharField(
        label = "Google Maps Api key:",
        required = False,
        widget = forms.TextInput(attrs={
            'class': 'form-control form',
            'type': 'text'
        }),
    )
    ZOOM_CHOICES = [(i, i) for i in range(19)]
    default_zoom = forms.ChoiceField(
        label = 'Default zoom',
        choices = ZOOM_CHOICES,
        required = False,
        widget = forms.Select(attrs={
            'class':'form-control form'
        }),
    )
    default_map = forms.ModelChoiceField(
        label = 'Default marker position',
        queryset = Overlay.objects.all(),
        required = True,
        widget = forms.Select(attrs={
            'class':'form-control form',
        }),
    )
    def __init__(self, *args, **kwargs):
        super(MapSettingsForm, self).__init__(*args, **kwargs)
        self.fields['default_map'].empty_label = None
        self.initial['google_maps_key'] = MapSettings.objects.first().google_maps_key
        self.initial['default_zoom'] = MapSettings.objects.first().default_zoom
        try:
            self.initial['default_map'] = Overlay.objects.get(
                centerx = MapSettings.objects.first().default_centerx, 
                centery = MapSettings.objects.first().default_centery
            ).pk
        except Overlay.DoesNotExist:
            self.initial['default_map'] = Overlay.objects.first()