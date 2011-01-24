"""This file provides the fetching and converting of the
feed from flickr.com.
"""

from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance
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
            format = 'json'
        )
        
    except Exception, exception:
        raise LoggedServiceError(original_exception = exception)

    # strip the jsonp leader and tail
    photos_json = photos_json.replace('jsonFlickrApi(', '')
    photos_json = photos_json.rstrip(')')
    
    try:
        photos = simplejson.loads(photos_json)
    except:
        return items

    if photos['photos'].has_key('photo'):
        for photo in photos['photos']['photo']:
            # flickr.photos.getInfo
            pic = flickr.photos_getInfo(photo_id=photo['id'], format='json')
            pic = pic.replace('jsonFlickrApi(', '')
            pic = pic.rstrip(')')
            pic_json = simplejson.loads(pic)
            epoch = pic_json['photo']['dateuploaded']
            created = datetime.fromtimestamp(float(epoch))
            
            # test if the pic is in our date range
            if created.date() > since - timedelta(days=1):
                item = ServiceItem()
                item.location = {}
                item.title = pic_json['photo']['title']['_content']
                item.body = pic_json['photo']['urls']['url'][0]['_content']
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
                item.url = "http://farm%s.static.flickr.com/%s/%s_%s_m_d.jpg" % \
                             (pic_json['photo']['farm'], 
                              pic_json['photo']['server'], 
                              pic_json['photo']['id'], 
                              pic_json['photo']['secret'])
                
                # add location
                if pic_json['photo'].has_key('location'):
                    item.location['lat'] = pic_json['photo']['location']['latitude']
                    item.location['long'] = pic_json['photo']['location']['longitude']
                    
                item.user = user
                items.append(item)
    
    return items
