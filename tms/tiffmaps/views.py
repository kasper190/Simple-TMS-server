from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    FormView,
    ListView,
)
from .forms import MapSettingsForm
from .models import (
    MapSettings,
    Overlay,
)
import os


class MapSettingsView(FormView):
    form_class = MapSettingsForm
    template_name = 'tiffmaps/mapsettings_view.html'
    success_url = reverse_lazy('tiffmaps:overlay-list')

    def get_context_data(self, **kwargs):
        context = super(MapSettingsView, self).get_context_data(**kwargs)
        context['overlay_first'] = Overlay.objects.first()
        return context

    def form_valid(self, form):
        default_map = form.cleaned_data['default_map']
        overlay_obj = Overlay.objects.get(mapname=default_map)
        map_settings_obj = MapSettings.objects.first()
        map_settings_obj.google_maps_key = form.cleaned_data['google_maps_key']
        map_settings_obj.default_zoom = form.cleaned_data['default_zoom']
        map_settings_obj.default_centerx = overlay_obj.centerx
        map_settings_obj.default_centery = overlay_obj.centery
        map_settings_obj.save()
        return super(MapSettingsView, self).form_valid(form)


class OverlayList(ListView):
    model = Overlay
    context_object_name = "overlays"
    template_name = 'tiffmaps/overlay_list.html'
    allow_empty = True

    def get_queryset(self):
        overlay_obj = Overlay.objects.all()
        ordering = self.request.GET.get('ordering', 'mapname')
        if ordering:
            overlay_obj = overlay_obj.order_by(ordering)
        return overlay_obj

    def get_context_data(self, **kwargs):
        context = super(OverlayList, self).get_context_data(**kwargs)
        context['ordering'] = self.request.GET.get('ordering', 'mapname')
        return context


class OverlayMetaView(View):
    def get(self, request, *args, **kwargs):
        settings_obj = MapSettings.objects.first()
        img_url = static('img/')
        maps_url = static('img/maps/')
        overlay_obj = Overlay.objects.values(
            'id', 'mapname', 'extension', 'created', 'publish', 
            'centerx', 'centery', 'minx', 'miny', 'maxx', 'maxy'
        )
        return JsonResponse({
            "default_centerx": settings_obj.default_centerx,
            "default_centery": settings_obj.default_centery,
            "default_zoom": settings_obj.default_zoom,
            "GOOGLE_MAPS_KEY": settings_obj.google_maps_key,
            "img_url": img_url,
            "maps_url": maps_url,
            "overlay": list(overlay_obj),
        })
