from datetime import datetime
import urllib2
import urllib
import json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.http import Http404
from django.core.cache import cache
import logging
 
from django.conf import settings

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
    

def display_albums(request, fb_id):
    """Fetch all facebook albums for specified id"""

    fql = "select aid, cover_pid, name, photo_count, created from album where owner=%s" % fb_id
    for blacklist in getattr(settings, 'FB_GALLERY_BLACKLIST', []):
        fql += " and not (name='%s')" % blacklist
    albums = get_fql_result(fql)
    for index, album in enumerate(albums):
        """ Store unix timestamp as datetime """
        album["date_created"] = datetime.fromtimestamp(int(album["created"]))
        """ Get the main photo for each Album """
        fql = "select src, src_big from photo where pid = '%s'" % album['cover_pid']
        for photo in get_fql_result(fql, timeout=cache.default_timeout*12*24):
            albums[index]['src'] = photo['src']
            albums[index]['src_big'] = photo['src_big']

    data = RequestContext(request, {
        'albums': albums,
        })
    
    return render_to_response('fbgallery/albums.html', context_instance=data)
    
    
def display_album(request, album_id, fb_id):
    """Display a facebook album

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