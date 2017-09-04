from datetime import datetime
import json
import logging
import urllib2
import urllib

from dateutil import parser
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
import facebook

logger = logging.getLogger(__name__)
fql_url = 'https://api.facebook.com/method/fql.query'


def get_fql_result(fql, timeout=cache.default_timeout*12):  # Without altering settings the default timeout=300
    cachekey = 'fbgallery_cache_' + slugify(fql)
    data = cache.get(cachekey)
    if data is None:
        logger.debug("Cache MISS for %s" % fql)
        options = {
            'query': fql,
            'format': 'json',
        }
        f = urllib2.urlopen(urllib2.Request(fql_url, urllib.urlencode(options)))
        response = f.read()
        f.close()  
        data = json.loads(response)
        cache.set(cachekey, data, timeout)
    return data
    

def album_listview(request):
    albums = cache.get('albums')
    if not albums:
        logger.debug("Cache MISS for 'albums'.") 
        graph = facebook.GraphAPI(version=settings.GRAPH_API_VERSION)
        response = graph.request('/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (settings.FB_APP_ID, settings.FB_APP_SECRET))
        graph = facebook.GraphAPI(access_token=response['access_token'], version=settings.GRAPH_API_VERSION)
        fb_albums = graph.request('%s/albums/' % settings.FB_PAGE_ID)['data']
        albums = []
        for fb_album in fb_albums:
            if fb_album['name'] in getattr(settings, 'FB_GALLERY_BLACKLIST', []):
                continue
            album = {}
            album['date_created'] = parser.parse(fb_album['created_time'])
            album['name'] = fb_album['name']
            album['id'] = fb_album['id']
            album_details = graph.request('%s?fields=cover_photo,photo_count' % album['id'])
            cover_id = album_details['cover_photo']['id']
            album['photo_count'] = album_details['photo_count']
            album['src'] = graph.request('%s?fields=images' % cover_id)['images'][0]['source']
            albums.append(album)
        cache.set('albums', albums, 1500)
    else:
        logger.debug("Cache HIT for 'albums'.")
    
    context = RequestContext(request, {'albums': albums})
    return render_to_response('fbgallery/albums.html', context_instance=context)


def album_detailview(request, pk):
    album = cache.get('album_%s' % pk)
    if not album:
        logger.debug("Cahce MISS for 'album_%s" % pk)
        graph = facebook.GraphAPI(version=settings.GRAPH_API_VERSION)
        response = graph.request('/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (settings.FB_APP_ID, settings.FB_APP_SECRET))
        graph = facebook.GraphAPI(access_token=response['access_token'], version=settings.GRAPH_API_VERSION)
        album_details = graph.request('%s?fields=name,photos{images}' % pk)
        images = [ image['images'][0]['source'] for image in album_details['photos']['data']]
        album = {}
        album['images'] = images
        album['name'] = album_details['name']
        cache.set('album_%s' % pk, album, 1500)

    context = RequestContext(request, {
        'album': album,
    })
    return render_to_response('fbgallery/album.html', context_instance=context)


def display_albums(request, fb_id):
    """Fetch all facebook albums for specified id"""

    fql = "select aid, cover_pid, name, photo_count, created from album where owner=%s" % fb_id
    for blacklist in getattr(settings, 'FB_GALLERY_BLACKLIST', []):
        fql += " and not (name='%s')" % blacklist
    albums = get_fql_result(fql)
    for index, album in enumerate(albums):
        # Store unix timestamp as datetime
        album["date_created"] = datetime.fromtimestamp(int(album["created"]))
        # Get the main photo for each Album
        fql = "select src, src_big from photo where pid = '%s'" % album['cover_pid']
        for photo in get_fql_result(fql, timeout=cache.default_timeout*12*24):
            albums[index]['src'] = photo['src']
            albums[index]['src_big'] = photo['src_big']

    data = RequestContext(request, {
        'albums': albums,
        })
    
    return render_to_response('fbgallery/albums.html', context_instance=data)
    
    
def display_album(request, album_id, fb_id):
    """
    Display a facebook album

    First check that the album id belongs to the page id specified
    """
    
    fql = "select aid, name from album where owner=%s and aid='%s'" % (fb_id, album_id)
    album = get_fql_result(fql)[0]
    if album:
        fql = "select pid, src, src_small, src_big, src_big_height, src_big_width, caption from photo where aid = '%s'  order by created desc" % album_id
        photos = get_fql_result(fql)
    else:
        raise Http404
    
    data = RequestContext(request, {
        'album': album,
        'photos': photos,
        })
    return render_to_response('fbgallery/album.html', context_instance=data)