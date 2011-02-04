"""This file provides the fetching and converting of the
feed from flickr.com.
"""

from causal.main.models import ServiceItem, AccessToken
from causal.main.utils.services import get_model_instance
from causal.main.exceptions import LoggedServiceError
from datetime import datetime, timedelta
from django.utils import simplejson
import flickrapi

DISPLAY_NAME = 'Flickr'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance):
    """Fetch and normalise the updates from the service."""

    serv = model_instance or get_model_instance(user, __name__)
    items = []

    access_token = AccessToken.objects.get(service=serv)
    flickr = flickrapi.FlickrAPI(access_token.api_token)

    try:
        photos_json = flickr.photos_search(
            user_id = access_token.userid,
            per_page = '10',
            format = 'json',
            nojsoncallback ='1'
        )

    except Exception, exception:
        raise LoggedServiceError(original_exception = exception)

    try:
        photos = simplejson.loads(photos_json)
    except:
        return items

    if photos['photos'].has_key('photo'):
        for photo in photos['photos']['photo']:

            # info about the pic
            pic = flickr.photos_getInfo(photo_id=photo['id'], format='json', nojsoncallback='1')
            pic_json = simplejson.loads(pic)

            epoch = pic_json['photo']['dateuploaded']
            created = datetime.fromtimestamp(float(epoch))

            # test if the pic is in our date range
            if created.date() > since - timedelta(days=1):
                item = ServiceItem()

                # info about how the pic was taken
                exif = flickr.photos_getExif(photo_id=photo['id'], format='json', nojsoncallback ='1')
                exif_json = simplejson.loads(exif)
                item.camera_make = _extract_camera_type(exif_json)

                item.location = {}
                item.title = pic_json['photo']['title']['_content']

                item.created = created
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

    make_model = None

    # first attempt using the "model"
    # second using "make"
    try:
        make_model = json['photo']['exif'][1]['raw']['_content']
        return make_model
    except:
        pass
    try:
        make_model =  json['photo']['exif'][0]['raw']['_content']
        return make_model
    except:
        pass
    return make_model


