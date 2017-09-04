from django.conf.urls import patterns, url
from django.conf import settings

fb_id = getattr(settings, 'FB_PAGE_ID', None)

urlpatterns = patterns(
    'fbgallery.views',
    url(r'^$', 'album_listview', name='fb-albums'),
    url(r'^(?P<pk>[-\w]+)/$', 'album_detailview', name='fb-album'),
)
