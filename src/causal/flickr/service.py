"""This file provides the fetching and converting of the
feed from flickr.com.
"""

from causal.main.models import ServiceItem, AccessToken
from causal.main.utils.services import get_model_instance
from causal.main.exceptions import LoggedServiceError
from datetime import datetime, timedelta
from django.utils import simplejson
import flickrapi
import time

DISPLAY_NAME = 'Flickr'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance):
    """Fetch and normalise the updates from the service."""

    serv = model_instance or get_model_instance(user, __name__)
    access_token = AccessToken.objects.get(service=serv)
    
    flickr = flickrapi.FlickrAPI(access_token.api_token)
    photos = _get_service_items(user, model_instance, flickr, serv, access_token)
    
    items = []

    if photos and photos['photos'].has_key('photo'):
        for photo in photos['photos']['photo']:

            # info about the pic
            pic = flickr.photos_getInfo(photo_id=photo['id'], format='json', nojsoncallback='1')
            pic_json = simplejson.loads(pic)
            
            item = ServiceItem()

            item.title = pic_json['photo']['title']['_content']
            
            # use date from when the photo was uploaded to flickr NOT when it was taken
            item.created = datetime.fromtimestamp(float(pic_json['photo']['dates']['posted'])) #u'posted': u'1300054696'
            
            item.service = serv

            item.link_back = pic_json['photo']['urls']['url'][0]['_content']
            item.tags = pic_json['photo']['tags']['tag']
            item.favorite = pic_json['photo']['isfavorite']

            item.url_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % \
                         (pic_json['photo']['farm'],
                          pic_json['photo']['server'],
                          pic_json['photo']['id'],
                          pic_json['photo']['secret'])

            item.url_small = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % \
                         (pic_json['photo']['farm'],
                          pic_json['photo']['server'],
                          pic_json['photo']['id'],
                          pic_json['photo']['secret'])

            item.body = "<br/><img src='" + item.url_thumb +"'/>"
            # add location

            item.user = user
            items.append(item)

    return items

def _get_service_items(user, model_instance, flickr, serv, access_token):
    """Helper method to fetch items for either history or stats page."""

    delta = timedelta(days=7)
    now = datetime.now()
    then = now - delta
    epoch_now = time.mktime(now.timetuple())
    epoch_then = time.mktime(then.timetuple())
    
    try:
        photos_json = flickr.photos_search(
            user_id = access_token.userid,
            per_page = '10',
            format = 'json',
            nojsoncallback ='1',
            min_upload_date = int(epoch_then),
            max_upload_date = int(epoch_now)
        )

    except Exception, exception:
        raise LoggedServiceError(original_exception = exception)

    try:
        return simplejson.loads(photos_json)
    except:
        return None

    
def _fetch_favorites(user_id, flickr):
    """Fetch the list of photos that the current use has made their fav."""
    
    delta = timedelta(days=7)
    now = datetime.now()
    then = now - delta
    epoch_now = time.mktime(now.timetuple())
    epoch_then = time.mktime(then.timetuple())
    
    favs = flickr.favorites_getList(user_id=user_id, 
                                    max_fave_date=int(epoch_now), 
                                    min_fave_date=int(epoch_then), 
                                    format='json', 
                                    nojsoncallback ='1')
    
    return simplejson.loads(favs)
    
def get_stats_items(user, since, model_instance):
    """Fetch and normalise the updates from the service and generate stats."""

    serv = model_instance or get_model_instance(user, __name__)
    access_token = AccessToken.objects.get(service=serv)
    
    flickr = flickrapi.FlickrAPI(access_token.api_token)
    photos = _get_service_items(user, model_instance, flickr, serv, access_token)
    
    items = []
    
    if photos and photos['photos'].has_key('photo'):
        for photo in photos['photos']['photo']:

            item = ServiceItem()            
            
            # info about the pic
            pic = flickr.photos_getInfo(photo_id=photo['id'], format='json', nojsoncallback='1')
            pic_json = simplejson.loads(pic)

            # info about how the pic was taken
            exif = flickr.photos_getExif(photo_id=photo['id'], format='json', nojsoncallback ='1')
            exif_json = simplejson.loads(exif)
            item.camera_make = _extract_camera_type(exif_json)
    
            item.location = {}
            item.title = pic_json['photo']['title']['_content']
    
            # use date from when the photo was uploaded to flickr NOT when it was taken
            item.created = datetime.fromtimestamp(float(pic_json['photo']['dates']['posted'])) #u'posted': u'1300054696'
            
            item.service = serv
    
            item.link_back = pic_json['photo']['urls']['url'][0]['_content']
            item.tags = pic_json['photo']['tags']['tag']
            item.favorite = pic_json['photo']['isfavorite']
    
            # add views
            item.views = pic_json['photo']['views']
    
            # add tags
            item.tags = pic_json['photo']['tags']['tag']
    
            if pic_json['photo']['comments']['_content'] == 0:
                item.number_of_comments = "No comments"
            else:
                item.number_of_comments = pic_json['photo']['comments']['_content']
    
            item.url_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % \
                         (pic_json['photo']['farm'],
                          pic_json['photo']['server'],
                          pic_json['photo']['id'],
                          pic_json['photo']['secret'])
    
            item.url_small = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % \
                         (pic_json['photo']['farm'],
                          pic_json['photo']['server'],
                          pic_json['photo']['id'],
                          pic_json['photo']['secret'])
    
            item.body = "<br/><img src='" + item.url_thumb +"'/>"
            # add location
            if pic_json['photo'].has_key('location'):
                item.location['lat'] = pic_json['photo']['location']['latitude']
                item.location['long'] = pic_json['photo']['location']['longitude']
    
            item.user = user
            items.append(item)
                    
        return items

def _extract_camera_type(json):
    """Return the make and model of a photo."""

    make_model = "Unknown make"

    # first attempt using the "model"
    # second using "make"
    try:
        if json['photo']['exif'][0]['tag'] == 'Make':
            make_model = json['photo']['exif'][1]['raw']['_content']
            return make_model
    except:
        pass
    try:
        if json['photo']['exif'][1]['tag'] == 'Model':
            make_model =  json['photo']['exif'][0]['raw']['_content']
            return make_model
    except:
        pass
    return make_model


