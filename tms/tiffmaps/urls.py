from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from .views import (
	MapSettingsView,
	OverlayMetaView,
    OverlayList,
)

urlpatterns = [
    url(r'^$', OverlayList.as_view(), name='overlay-list'),
    url(r'^metadata/$', OverlayMetaView.as_view(), name='overlay-meta-view'),
    url(r'^settings/$', MapSettingsView.as_view(), name='map-settings-view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        url(r'^static/(.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),
        url(r'^media/(.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
	]